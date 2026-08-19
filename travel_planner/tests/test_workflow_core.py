import unittest

from src.travel_planner.agents.budget_agent import budget_agent
from src.travel_planner.agents.final_planner import final_planner
from src.travel_planner.state.TripState import TripState


class WorkflowCoreTests(unittest.TestCase):
    def test_complete_cost_data_within_budget(self):
        state = TripState(
            budget=1000,
            flight_results=[{"price": 600}],
            hotel_results=[{"name": "Test Hotel", "total_price": 300}],
            activities=[{"name": "Museum", "cost": 50}],
        )

        result = budget_agent(state)

        self.assertEqual(result.total_cost, 950.0)
        self.assertEqual(result.budget_status, "within_budget")
        self.assertTrue(result.cost_data_complete)
        self.assertTrue(result.is_within_budget)

    def test_missing_provider_results_are_incomplete(self):
        result = budget_agent(TripState(budget=1000))

        self.assertEqual(result.budget_status, "incomplete")
        self.assertFalse(result.cost_data_complete)
        self.assertFalse(result.is_within_budget)
        self.assertIn("required travel results are missing", result.budget_message)

    def test_over_budget_sets_recommendations_when_options_exist(self):
        state = TripState(
            budget=800,
            flight_results=[{"price": 600}, {"price": 500}],
            hotel_results=[{"name": "Expensive Hotel", "total_price": 400}, {"name": "Cheaper Hotel", "total_price": 300}],
        )

        result = budget_agent(state)

        self.assertEqual(result.budget_status, "over_budget")
        self.assertFalse(result.is_within_budget)
        self.assertEqual(result.total_cost, 1000.0)
        self.assertEqual(len(result.cost_saving_recommendations), 2)

    def test_final_plan_reports_missing_results(self):
        result = final_planner(budget_agent(TripState(destination="Paris")))

        self.assertIn("Trip to Paris", result.final_plan)
        self.assertIn("Flight: no offer returned", result.final_plan)
        self.assertIn("Budget status: incomplete", result.final_plan)


if __name__ == "__main__":
    unittest.main()
