"""Exact signed-anchor identities, independent codegrees and rejection tests."""
from collections import Counter
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "anchor_graph", ROOT / "constructions/sections/d45/verify_parent.py")
ANCHOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANCHOR)


class AnchorGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = ANCHOR.check()
        parent = json.loads((ANCHOR.DATA / "parent.json").read_text())
        p = np.array(parent["parent_coeff"], dtype=np.int64)
        g = np.array(json.loads((ANCHOR.DATA / "gram.json").read_text())["ambient_G"],
                     dtype=np.int64)
        rows = [tuple(json.loads(line)) for line in
                (ANCHOR.DATA / "parent-vectors.jsonl").read_text().splitlines() if line.strip()]
        reps = sorted({min(row, tuple(p-np.array(row))) for row in rows})
        u = np.array(reps, dtype=np.int64)
        cls.signed = u @ g @ u.T - 2
        np.fill_diagonal(cls.signed, 0)

    def test_exact_frame_spectrum_and_fixed_anchor_optimum(self):
        report = self.report
        graph = report["graph_structure"]
        self.assertEqual(ANCHOR.anchor_moments(), (90961920, 2256, 192))
        self.assertEqual((report["one_endpoint_frame_constant"], report["frame_dimension"]),
                         (96, 47))
        self.assertTrue(report["physical_tight_frame_checked"])
        self.assertEqual(graph["signed_spectrum"],
                         [{"eigenvalue": -4, "multiplicity": 1081},
                          {"eigenvalue": 92, "multiplicity": 47}])
        self.assertEqual(graph["unsigned_eigenvalue_lower_bound"], -16)
        self.assertEqual(graph["nonadjacent_pairs"], 428076)
        self.assertEqual(graph["adjacent_pairs"], 207552)
        self.assertEqual(graph["nonadjacent_codegree_minimum"], 70)
        self.assertEqual(graph["nonadjacent_codegree_minimum_multiplicity"], 1)
        self.assertEqual(graph["nonadjacent_codegree_maximum"], 148)
        self.assertEqual(report["fixed_anchor_maximum_projected_count"], 7380090)
        self.assertEqual(report["all_section_counts_divisible_by"], 18)
        self.assertEqual(graph["negative_four_cliques"], 0)
        self.assertEqual((graph["positive_triangles"], graph["negative_triangles"]),
                         (7528040, 1439848))

    def test_all_codegrees_against_independent_python_bitsets(self):
        # This neither multiplies adjacency matrices nor uses fixed histogram
        # values: it recounts every unordered pair by arbitrary-size integers.
        neighbours = [sum(1 << int(j) for j in np.flatnonzero(row))
                      for row in self.signed]
        adjacent, nonadjacent = Counter(), Counter()
        for i, row in enumerate(self.signed):
            for j in range(i+1, len(row)):
                common = (neighbours[i] & neighbours[j]).bit_count()
                (adjacent if row[j] else nonadjacent)[common] += 1
        self.assertEqual(dict(adjacent), self.report["graph_structure"]["adjacent_codegree_histogram"])
        self.assertEqual(dict(nonadjacent), self.report["graph_structure"]["nonadjacent_codegree_histogram"])
        self.assertTrue(all(c % 2 == 0 for c in adjacent.keys() | nonadjacent.keys()))
        self.assertTrue(all((7380720-9*c) % 18 == 0 for c in nonadjacent))

    def test_switching_preserves_spectrum_and_all_graph_counts(self):
        signs = np.where(np.arange(len(self.signed)) % 7 < 3, -1, 1)
        switched = signs[:, None] * self.signed * signs[None, :]
        report, _, _ = ANCHOR.check_signed_graph(switched)
        self.assertEqual(report, self.report["graph_structure"])

    def test_single_edge_sign_corruption_is_rejected(self):
        corrupted = self.signed.copy()
        i, j = next(zip(*np.nonzero(np.triu(corrupted, 1))))
        corrupted[i, j] *= -1
        corrupted[j, i] *= -1
        # Degree and every unsigned codegree are unchanged by this corruption.
        with self.assertRaisesRegex(ValueError, "Signed quadratic identity"):
            ANCHOR.check_signed_graph(corrupted)

    def test_noninteger_and_asymmetric_signed_matrices_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "integer 1128"):
            ANCHOR.check_signed_graph(self.signed.astype(float))
        corrupted = self.signed.copy()
        corrupted[0, 1] = 1 if corrupted[1, 0] != 1 else -1
        with self.assertRaisesRegex(ValueError, "symmetry or diagonal"):
            ANCHOR.check_signed_graph(corrupted)

    def test_negative_four_clique_checker_on_every_signed_four_vertex_graph(self):
        edges = list(combinations(range(4), 2))
        triangles = list(combinations(range(4), 3))
        for values in product((-1, 0, 1), repeat=6):
            signed = np.zeros((4, 4), dtype=np.int32)
            for (i, j), value in zip(edges, values):
                signed[i, j] = signed[j, i] = value
            negative_triangles = sum(signed[i, j]*signed[j, k]*signed[k, i] == -1
                                     for i, j, k in triangles)
            # An all-negative switching exists iff every triangle is negative.
            if negative_triangles == 4:
                with self.assertRaisesRegex(ValueError, "negative four-clique"):
                    ANCHOR.check_negative_four_cliques(signed)
            else:
                self.assertEqual(ANCHOR.check_negative_four_cliques(signed), negative_triangles)

    def test_corrupted_physical_basis_and_repeated_endpoint_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            for name in ("parent.json", "gram.json", "parent-vectors.jsonl"):
                shutil.copyfile(ANCHOR.DATA / name, data / name)
            parent = json.loads((data / "parent.json").read_text())
            parent["basis_scaled_by_sqrt12"][0][0] += 1
            (data / "parent.json").write_text(json.dumps(parent))
            with self.assertRaisesRegex(ValueError, "Physical basis differs"):
                ANCHOR.check(data)
            shutil.copyfile(ANCHOR.DATA / "parent.json", data / "parent.json")
            rows = (data / "parent-vectors.jsonl").read_text().splitlines()
            rows[0] = rows[1]
            (data / "parent-vectors.jsonl").write_text("\n".join(rows) + "\n")
            with self.assertRaisesRegex(ValueError, "Repeated parent endpoint"):
                ANCHOR.check(data)


if __name__ == "__main__":
    unittest.main()
