import os
import sys
import unittest
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import pipeline  # noqa: E402

CSV = os.path.join(ROOT, "data", "example_leads.csv")


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.leads = pipeline.load_leads(CSV)

    def test_conversion_counts(self):
        reached, rates = pipeline.conversion_rates(self.leads)
        self.assertEqual(reached, [18, 15, 9, 6, 3])
        self.assertAlmostEqual(rates[-1][4], 0.5)

    def test_weekly_targets(self):
        t = pipeline.weekly_targets(30000, 10000, 0.25, 0.10)
        self.assertEqual(t["deals_month"], 3)
        self.assertEqual(t["conversations_month"], 12)
        self.assertEqual(t["outreach_month"], 120)
        self.assertEqual(t["outreach_week"], 28)

    def test_stale_leads(self):
        stale = pipeline.stale_leads(self.leads, date(2026, 10, 5))
        self.assertEqual({l["id"] for l, _, _ in stale}, {"L02", "L03", "L09", "L11", "L12", "L16"})


if __name__ == "__main__":
    unittest.main()
