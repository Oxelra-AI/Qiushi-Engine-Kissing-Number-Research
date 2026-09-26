"""Consistency of the bilingual reports, result tables and public links."""
import json
from pathlib import Path
import re
import unittest
import hashlib
import ast
import operator

ROOT = Path(__file__).resolve().parents[1]


class Documents(unittest.TestCase):
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
