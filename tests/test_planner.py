import unittest

from app import app
from planner import PlanRequest, generate_week_plan
from planner.catalog import DAYS


class WeekPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.req = PlanRequest(budget=75, max_stores=2)
        cls.plan = generate_week_plan(cls.req)

    def test_full_week_with_three_meals(self):
        self.assertEqual([d["day"] for d in self.plan["week"]], list(DAYS))
        for day in self.plan["week"]:
            self.assertEqual([m["meal"] for m in day["meals"]], ["breakfast", "lunch", "dinner"])
            for m in day["meals"]:
                self.assertGreater(m["calories"], 0)
                self.assertGreater(m["protein"], 0)
                self.assertGreaterEqual(m["cost"], 0)

    def test_within_budget_and_store_limit(self):
        s = self.plan["summary"]
        self.assertLessEqual(s["total_cost"], self.req.budget)
        self.assertLessEqual(len(s["stores"]), self.req.max_stores)

    def test_tracking_balances(self):
        for t in self.plan["tracking"]:
            used = sum(u["grams"] for u in t["uses"])
            self.assertAlmostEqual(t["purchased_g"] - used, t["remaining_g"], delta=1)
            self.assertGreaterEqual(t["remaining_g"], 0)

    def test_ingredients_are_reused(self):
        multi = [t for t in self.plan["tracking"] if t["meal_count"] >= 3]
        self.assertGreaterEqual(len(multi), 5)
        reused_meals = sum(1 for d in self.plan["week"] for m in d["meals"] if m["reused"])
        self.assertGreater(reused_meals, 15)

    def test_pantry_staples_not_in_budget_by_default(self):
        self.assertEqual(self.plan["pantry"]["label"], "Pantry Staples (Assumed Available)")
        pantry_names = {p["name"] for p in self.plan["pantry"]["items"] if not p["buy"]}
        shop_names = {s["ingredient"] for s in self.plan["shopping_list"]}
        self.assertFalse(pantry_names & shop_names)

    def test_summary_text(self):
        text = self.plan["summary"]["text"]
        self.assertIn("for the week", text)
        self.assertIn("on promotion", text)
        self.assertIn("supermarket", text)


class CalorieTargetTests(unittest.TestCase):
    def test_days_match_calorie_target(self):
        for target in (1600, 3000):
            plan = generate_week_plan(PlanRequest(kcal_target=target, budget=150))
            for day in plan["week"]:
                self.assertAlmostEqual(day["calories"], target, delta=target * 0.03)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_rejects_out_of_range(self):
        res = self.client.post("/api/plan", json={"people": 50})
        self.assertEqual(res.status_code, 400)

    def test_rejects_non_numeric(self):
        res = self.client.post("/api/plan", json={"budget": "abc"})
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
