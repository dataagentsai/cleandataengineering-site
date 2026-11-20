"""Table-driven checks for the fundamentals pages.   python3 -m unittest _guides/test_fundamentals.py -v"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fundamentals_data import PAGES  # noqa: E402

RULES = Path.home() / "CostLens/costlens-core/rule_docs"
SLUGS = ["performance", "cost", "processing", "security", "storage", "database-families"]
FIELDS = ["slug", "short", "title", "desc", "lede", "physics", "mindmap", "sections", "rules", "faq"]


class Fundamentals(unittest.TestCase):
    def test_pages_present(self):
        self.assertEqual([p["slug"] for p in PAGES], SLUGS)

    def test_table_driven(self):
        cases = [
            ("required fields", lambda p: all(p.get(f) for f in FIELDS)),
            ("five physics facts", lambda p: len(p["physics"]) == 5),
            ("mind map has 7-8 branches", lambda p: 7 <= len(p["mindmap"]) <= 8),
            ("mind map rows are 4-tuples", lambda p: all(len(r) == 4 for r in p["mindmap"])),
            ("section rows match header width", lambda p: all(len(r) == len(s[4]) for s in p["sections"] for r in s[5])),
            ("section ids unique", lambda p: len({s[0] for s in p["sections"]}) == len(p["sections"])),
            ("at least 6 faq entries", lambda p: len(p["faq"]) >= 6),
            ("desc within 160 chars-ish", lambda p: len(p["desc"]) <= 320),
        ]
        for slug_page in PAGES:
            for name, check in cases:
                with self.subTest(page=slug_page["slug"], case=name):
                    self.assertTrue(check(slug_page))

    @unittest.skipUnless(RULES.exists(), "CostLens rule_docs not on this machine")
    def test_rule_ids_exist(self):
        for p in PAGES:
            for cat, rows in p["rules"]:
                for rid, _ in rows:
                    with self.subTest(page=p["slug"], rule=rid):
                        self.assertTrue((RULES / f"{rid}.yaml").exists())


if __name__ == "__main__":
    unittest.main()
