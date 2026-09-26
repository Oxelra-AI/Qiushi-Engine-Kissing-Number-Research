"""Consistency of the bilingual reports, result tables and public links."""
import json
from pathlib import Path
import re
import unittest
import hashlib
import ast
import operator
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]


class Documents(unittest.TestCase):
    def test_dimensional_research_accounts_and_navigation(self):
        expected = {32: 347584, 33: 363968, 34: 384196, 35: 409676, 36: 484760,
                    37: 498024, 38: 591900, 39: 763668, 43: 2553792, 45: 7380090}
        for suffix in (".md", ".zh-CN.md"):
            index = (ROOT / "research" / ("README" + suffix)).read_text()
            homepage = (ROOT / ("README" + suffix)).read_text()
            paths = {path.name for path in (ROOT / "research/dimensions").glob("*" + suffix)
                     if suffix != ".md" or not path.name.endswith(".zh-CN.md")}
            self.assertEqual(paths, {str(d) + suffix for d in expected})
            for dimension, bound in expected.items():
                relative = f"dimensions/{dimension}{suffix}"
                text = (ROOT / "research" / relative).read_text()
                self.assertIn(f"]({relative})", index)
                self.assertIn(f"](research/{relative})", homepage)
                self.assertIn(r"\boxed{" + str(bound) + "}", text)
                self.assertIn("../../constructions/", text)
                other = ".zh-CN.md" if suffix == ".md" else ".md"
                self.assertIn(f"]({dimension}{other})", text)

    def test_shared_blocker_counts_in_the_research_accounts(self):
        root = ROOT / "constructions/codes"
        entries = json.loads((root / "data/exchanges/exchanges.json").read_text())["exchanges"]
        expected = {33: (10, 9, 20, {1: 1, 2: 8, 3: 1}),
                    34: (7, 6, 9, {1: 6, 3: 1}),
                    37: (40, 37, 84, {1: 8, 2: 22, 3: 8, 4: 2}),
                    39: (15, 14, 30, {1: 1, 2: 13, 3: 1})}
        for entry in entries:
            if entry["dimension"] not in expected:
                continue
            parent = [int(line, 16) for line in (root / entry["parent"]).read_text().splitlines()
                      if line.strip() and not line.startswith(("#", "$"))]
            additions = [int(value, 16) for value in entry["added_hex"]]
            blockers = [{a for a in parent if (a & b).bit_count() > 4} for b in additions]
            union = set().union(*blockers)
            actual = (len(additions), len(union), sum(map(len, blockers)),
                      dict(Counter(map(len, blockers))))
            self.assertEqual(actual, expected[entry["dimension"]])
            self.assertEqual(union, {int(value, 16) for value in entry["removed_hex"]})
            if entry["dimension"] == 33:
                self.assertEqual(max(Counter(a for group in blockers for a in group).values()), 4)

    def test_saved_search_distinguishes_relaxation_from_construction(self):
        record = json.loads((ROOT / "research/data/d34-exchange-search.json").read_text())
        self.assertEqual(record["dimension"], 34)
        for key in ("parent", "exchange"):
            self.assertTrue((ROOT / record[key]).is_file())
        first, final = record["iterations"]
        self.assertFalse(first["internally_compatible"])
        self.assertEqual(first["new_packing_constraints"], first["repeated_five_subset_keys"])
        self.assertTrue(final["internally_compatible"])
        self.assertEqual(final["repeated_five_subset_keys"], 0)
        for iteration in record["iterations"]:
            self.assertEqual(iteration["selected_candidates"] - iteration["deleted_old_supports"],
                             iteration["objective"])
        self.assertEqual(record["parent_size"] + final["objective"], record["final_size"])
        exchange = next(row for row in json.loads((ROOT / record["exchange"]).read_text())["exchanges"]
                        if row["dimension"] == 34)
        self.assertEqual(len(exchange["added_hex"]), final["selected_candidates"])
        self.assertEqual(len(exchange["removed_hex"]), final["deleted_old_supports"])

    def test_livestream_citation_uses_original_article(self):
        source = "https://hznews.hangzhou.com.cn/kejiao/content/2026-09/23/content_9314105.htm"
        for name in ("README.md", "README.zh-CN.md", "research/livestream.md"):
            self.assertIn(source, (ROOT / name).read_text(), name)

    def test_report_tables_match_catalogue(self):
        catalog = json.loads((ROOT / "constructions/catalog/results.json").read_text())
        expected = [(r["dimension"], r["lower_bound"], r["comparison"]["lower_bound"],
                     r["comparison"]["gain"]) for r in catalog["results"]]
        self.assertEqual(catalog["result_count"], len(expected))
        for language in ("en", "zh"):
            text = (ROOT / "reports" / language / "sections/results.tex").read_text()
            rows = re.findall(r"^(\d+) & (\d+) & (\d+) & (\d+) & \\cite\{[^}]+\} \\\\", text, re.M)
            self.assertEqual([tuple(map(int, row)) for row in rows], expected)
        for filename in ("README.md", "README.zh-CN.md", "research/results.md"):
            rows = re.findall(r"^\| (\d+) \| ([\d,]+) \| ([\d,]+) \| \+([\d,]+) \|$",
                              (ROOT / filename).read_text(), re.M)
            self.assertEqual([tuple(int(n.replace(",", "")) for n in row) for row in rows], expected)
        for _, bound, comparator, gain in expected:
            self.assertEqual(bound - comparator, gain)

    def test_bilingual_structure_matches(self):
        for relative in ("sections/constructions.tex", "latex/collection.tex", "refs.bib"):
            self.assertEqual((ROOT / "reports/en" / relative).read_bytes(),
                             (ROOT / "reports/zh" / relative).read_bytes(), relative)
        en = (ROOT / "reports/en/main.tex").read_text()
        zh = (ROOT / "reports/zh/main.tex").read_text()
        self.assertEqual(re.findall(r"\\input\{([^}]+)\}", en),
                         re.findall(r"\\input\{([^}]+)\}", zh))
        for language in ("en", "zh"):
            report = ROOT / "reports" / language
            for path in report.rglob("*.tex"):
                for target in re.findall(r"\\input\{([^}]+)\}", path.read_text()):
                    self.assertTrue((report / (target + ".tex")).is_file(), str(path) + ":" + target)

    def test_citations_have_bibliography_entries(self):
        for language in ("en", "zh"):
            report = ROOT / "reports" / language
            keys = set(re.findall(r"@\w+\{([^,]+),", (report / "refs.bib").read_text()))
            for path in report.rglob("*.tex"):
                for group in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", path.read_text()):
                    self.assertLessEqual(set(group.split(",")), keys, str(path))

    def test_paper_table_when_present(self):
        paper = ROOT / "paper/sections/introduction.tex"
        if not paper.is_file():
            self.skipTest("This collection contains reports and construction data")
        catalog = json.loads((ROOT / "constructions/catalog/results.json").read_text())
        expected = [(r["dimension"], r["lower_bound"]) for r in catalog["results"]]
        rows = re.findall(r"^(\d+)&(\d+)&", paper.read_text(), re.M)
        self.assertEqual([(int(d), int(n)) for d, n in rows], expected)

    def test_relative_document_links(self):
        paths = [ROOT / "README.md", ROOT / "README.zh-CN.md", ROOT / "RIGHTS.md"]
        for name in ("reports", "research", "evidence", "reproducibility", "constructions", "paper"):
            if (ROOT / name).exists():
                paths += list((ROOT / name).rglob("*.md"))
        for path in paths:
            for target in re.findall(r"\]\(([^\s)]+)\)", path.read_text()):
                if ":" in target or target.startswith("#"):
                    continue
                linked = path.parent / target.split("#")[0]
                if linked.suffix == ".pdf":
                    self.assertTrue(linked.with_suffix(".tex").is_file(), str(linked))
                else:
                    self.assertTrue(linked.exists(), str(linked))

    def test_report_front_matter_and_sources(self):
        for language in ("en", "zh"):
            report = ROOT / "reports" / language
            main = (report / "main.tex").read_text()
            self.assertIn(r"\input{latex/authors}", main)
            self.assertIn(r"\input{sections/abstract}", main)
            self.assertIn(r"\tableofcontents", main)
            authors = (report / "latex/authors.tex").read_text()
            self.assertIn("hansomchen@zju.edu.cn", authors)
            self.assertIn("yangyihao@zju.edu.cn", authors)
            self.assertTrue((report / "figures/qiushi-engine-logo.png").is_file())
        self.assertIn("接吻数新下界的自主发现", (ROOT / "reports/zh/main.tex").read_text())
        self.assertIn("Autonomous Discovery of New Lower Bounds", (ROOT / "reports/en/main.tex").read_text())
        self.assertIn("编码构造、格提升与截面计数", (ROOT / "reports/zh/main.tex").read_text())

    def test_report_date_and_author_order(self):
        expected = ("Shuxing Yang, Rui Zhao, Junyao Wu, Yize Wang, Fujia Chen, Kaihao Zhu, "
                    "Wenhao Li, Zichen Li, Yaqi Li, Shenzhan Hong, Yuang Pan, Junjie Yang, "
                    "Taowen Deng, Jincheng Mi, Hongsheng Chen, Yihao Yang")
        for language in ("en", "zh"):
            text = (ROOT / "reports" / language / "latex/authors.tex").read_text()
            self.assertIn(r"\newcommand{\ReportAuthorNames}{" + expected + "}", text)
            main = (ROOT / "reports" / language / "main.tex").read_text()
            self.assertIn("25 September 2026" if language == "en" else "2026年9月25日", main)
        cff = (ROOT / "CITATION.cff").read_text()
        names = re.findall(r"  - family-names: (.+)\n    given-names: (.+)", cff)
        self.assertEqual(", ".join(given + " " + family for family, given in names), expected)

    def test_mathematical_inputs_are_present(self):
        catalog = json.loads((ROOT / "constructions/catalog/results.json").read_text())
        for row in catalog["results"]:
            for relative in row["artifact_ids"]:
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_artifact_identities(self):
        catalogue = json.loads((ROOT / "constructions/catalog/artifacts.json").read_text())
        for entry in catalogue["artifacts"]:
            path = ROOT / entry["path"]
            self.assertEqual(path.stat().st_size, entry["bytes"], entry["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"], entry["path"])

    def test_count_formulas_and_proof_map(self):
        operations = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul}
        def integer_expression(node):
            if isinstance(node, ast.Constant) and type(node.value) is int:
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in operations:
                return operations[type(node.op)](integer_expression(node.left), integer_expression(node.right))
            raise ValueError("Expected an integer sum or product")
        catalogue = json.loads((ROOT / "constructions/catalog/results.json").read_text())
        proof = (ROOT / "evidence/proof-map.md").read_text()
        dimensions = [r["dimension"] for r in catalogue["results"]]
        self.assertEqual([int(d) for d in re.findall(r"^### Dimension (\d+)$", proof, re.M)], dimensions)
        for row in catalogue["results"]:
            value = integer_expression(ast.parse(row["count_formula"], mode="eval").body)
            self.assertEqual(value, row["lower_bound"])
            self.assertIn(row["count_formula"], proof)

    def test_source_copy_identities(self):
        for manifest in ROOT.glob("constructions/**/source-manifest.json"):
            for entry in json.loads(manifest.read_text())["files"]:
                path = manifest.parent / entry["path"]
                self.assertTrue(path.is_file(), str(path))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"], str(path))


if __name__ == "__main__":
    unittest.main()
