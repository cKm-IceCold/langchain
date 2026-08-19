import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

AMADEUS_BASE_URL = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com")
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
REQUEST_TIMEOUT_SECONDS = int(os.getenv("TRAVEL_API_TIMEOUT_SECONDS", "20"))
MAX_RETRIES = int(os.getenv("TRAVEL_API_MAX_RETRIES", "2"))
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_last_nominatim_request_at = 0.0

_amadeus_token: Optional[str] = None
_amadeus_token_expires_at = datetime.min


class TravelApiError(RuntimeError):
    """Raised when a travel provider cannot return usable data."""


def _request_json(
    url: str,
    *,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[bytes] = None,
    timeout: int = REQUEST_TIMEOUT_SECONDS,
) -> Dict[str, Any] | List[Any]:
    request = Request(url, headers=headers or {}, data=data, method=method)
    for attempt in range(MAX_RETRIES + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code not in RETRYABLE_STATUS_CODES or attempt >= MAX_RETRIES:
                raise TravelApiError(f"Travel provider request failed with HTTP {exc.code}.") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt >= MAX_RETRIES:
                raise TravelApiError(f"Travel provider request failed: {exc}") from exc
        time.sleep(2**attempt)

    raise TravelApiError("Travel provider request failed after retries.")


def _amadeus_access_token() -> str:
    global _amadeus_token, _amadeus_token_expires_at

    if _amadeus_token and datetime.utcnow() < _amadeus_token_expires_at:
        return _amadeus_token

    client_id = os.getenv("AMADEUS_CLIENT_ID")
    client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise TravelApiError(
            "AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET are required for flight and hotel search."
        )

    payload = urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")
    response = _request_json(
        f"{AMADEUS_BASE_URL}/v1/security/oauth2/token",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=payload,
    )

    if not isinstance(response, dict) or "access_token" not in response:
        raise TravelApiError("Amadeus returned an invalid access-token response.")

    _amadeus_token = str(response["access_token"])
    expires_in = int(response.get("expires_in", 1200))
    _amadeus_token_expires_at = datetime.utcnow() + timedelta(seconds=max(60, expires_in - 60))
    return _amadeus_token


def _amadeus_get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    token = _amadeus_access_token()
    query = urlencode({key: value for key, value in params.items() if value not in (None, "")})
    response = _request_json(
        f"{AMADEUS_BASE_URL}{path}?{query}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if not isinstance(response, dict):
        raise TravelApiError("Amadeus returned an unexpected response.")
    return response


def _resolve_city_code(city: str) -> str:
    response = _amadeus_get(
        "/v1/reference-data/locations",
        {"subType": "CITY", "keyword": city, "page[limit]": 1},
    )
    locations = response.get("data", [])
    if not locations:
        raise TravelApiError(f"Amadeus could not resolve city: {city}")
    return str(locations[0].get("iataCode", ""))


def search_flights(
    departure_city: str,
    destination: str,
    departure_date: str,
    return_date: str,
    travelers: int,
    budget: float,
) -> List[Dict[str, Any]]:
    origin_code = _resolve_city_code(departure_city)
    destination_code = _resolve_city_code(destination)
    response = _amadeus_get(
        "/v2/shopping/flight-offers",
        {
            "originLocationCode": origin_code,
            "destinationLocationCode": destination_code,
            "departureDate": departure_date,
            "returnDate": return_date,
            "adults": max(1, travelers),
            "currencyCode": "USD",
            "max": 10,
        },
    )

    results = []
    for offer in response.get("data", []):
        itineraries = offer.get("itineraries", [])
        outbound = itineraries[0].get("segments", []) if itineraries else []
        if not outbound:
            continue
        first_segment = outbound[0]
        last_segment = outbound[-1]
        total_price = float(offer.get("price", {}).get("grandTotal", 0))
        if budget > 0 and total_price > budget:
            continue
        results.append(
            {
                "source": "Amadeus free test API",
                "airline": first_segment.get("carrierCode", "Unknown"),
                "price": total_price,
                "departure_time": first_segment.get("departure", {}).get("at", ""),
                "arrival_time": last_segment.get("arrival", {}).get("at", ""),
                "duration": itineraries[0].get("duration", "") if itineraries else "",
                "route": f"{origin_code} -> {destination_code}",
                "departure_date": departure_date,
                "return_date": return_date,
            }
        )

    return sorted(results, key=lambda item: item["price"])


def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    travelers: int,
    budget: float,
) -> List[Dict[str, Any]]:
    city_code = _resolve_city_code(destination)
    locations = _amadeus_get(
        "/v1/reference-data/locations/hotels/by-city",
        {"cityCode": city_code, "radius": 20, "radiusUnit": "KM", "hotelSource": "ALL"},
    )
    hotel_ids = [item.get("hotelId") for item in locations.get("data", [])[:10] if item.get("hotelId")]
    if not hotel_ids:
        return []

    response = _amadeus_get(
        "/v3/shopping/hotel-offers",
        {
            "hotelIds": ",".join(hotel_ids),
            "checkInDate": check_in,
            "checkOutDate": check_out,
            "adults": max(1, travelers),
            "roomQuantity": 1,
            "currency": "USD",
        },
    )

    results = []
    for item in response.get("data", []):
        hotel = item.get("hotel", {})
        offers = item.get("offers", [])
        if not offers:
            continue
        offer = offers[0]
        price = float(offer.get("price", {}).get("total", 0))
        if budget > 0 and price > budget:
            continue
        results.append(
            {
                "source": "Amadeus free test API",
                "name": hotel.get("name", "Unknown hotel"),
                "total_price": price,
                "price_per_night": price / max(1, _nights_between(check_in, check_out)),
                "rating": hotel.get("rating"),
                "location": hotel.get("address", {}).get("cityName", destination),
                "check_in": check_in,
                "check_out": check_out,
            }
        )

    return sorted(results, key=lambda item: item["total_price"])


def _nights_between(check_in: str, check_out: str) -> int:
    try:
        return max(1, (datetime.fromisoformat(check_out) - datetime.fromisoformat(check_in)).days)
    except ValueError:
        return 1


def search_activities(destination: str, preferences: List[str]) -> List[Dict[str, Any]]:
    global _last_nominatim_request_at

    search_terms = preferences or ["tourist attraction", "museum", "park"]
    results: List[Dict[str, Any]] = []
    seen_names = set()

    for term in search_terms[:3]:
        elapsed = time.monotonic() - _last_nominatim_request_at
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        query = urlencode({"q": f"{term} in {destination}", "format": "jsonv2", "limit": 5})
        request = Request(
            f"{NOMINATIM_URL}?{query}",
            headers={"User-Agent": "travel-planner-learning-app/1.0"},
        )
        response = _request_json(request.full_url, headers=dict(request.headers))
        _last_nominatim_request_at = time.monotonic()
        if not isinstance(response, list):
            continue
        for place in response:
            name = str(place.get("display_name", "")).split(",")[0].strip()
            if not name or name in seen_names:
                continue
            seen_names.add(name)
            results.append(
                {
                    "source": "OpenStreetMap Nominatim",
                    "name": name,
                    "category": term,
                    "location": place.get("display_name", ""),
                    "latitude": place.get("lat"),
                    "longitude": place.get("lon"),
                    "cost": None,
                    "duration": None,
                }
            )

    return results
