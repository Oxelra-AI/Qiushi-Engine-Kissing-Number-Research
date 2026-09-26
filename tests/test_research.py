"""Exact checks of the finite calculations used in the research accounts."""
from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_support_regions import check as check_regions


class ResearchCalculations(unittest.TestCase):
    def test_section_signature_domain(self):
        # H = 8I - 2J, H^{-1} = (I + J)/8.
        roots = [z for z in product(range(-1, 2), repeat=3)
                 if 8 * sum(a*a for a in z) - 2 * sum(z)**2 == 6]
        exceptional = {tuple(8*a - 2*sum(z) for a in z) for z in roots}
        domain = {y for y in product(range(-6, 7), repeat=3)
                  if sum(a*a for a in y) + sum(y)**2 <= 48
                  and (y in exceptional or all(abs(sum(a*b for a, b in zip(y, z))) <= 3
                                               for z in roots))}
        ordinary = domain - exceptional
        representatives = sorted({min(y, tuple(-a for a in y)) for y in ordinary})
        moments = [a for a in product(range(11), repeat=3)
                   if sum(a) <= 10 and sum(a) % 2 == 0]
        self.assertEqual((len(roots), len(exceptional), len(domain), len(ordinary)),
                         (8, 8, 239, 231))
        self.assertIn((0, 0, 0), ordinary)
        self.assertEqual((len(representatives), len(moments)), (116, 161))
        saved = json.loads((ROOT / "constructions/sections/d45/data/dual.json").read_text())
        self.assertEqual([list(y) for y in representatives], saved["signature_representatives"])
        self.assertEqual([list(a) for a in moments], saved["moment_multi_indices"])

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy is required")
    def test_witnesses_are_a_neighbourhood_difference(self):
        import numpy as np
        data = ROOT / "constructions/sections/d45/data"
        parent = json.loads((data / "parent.json").read_text())
        G = np.array(json.loads((data / "gram.json").read_text())["ambient_G"], dtype=np.int64)
        p = np.array(parent["parent_coeff"], dtype=np.int64)
        r, s = (np.array(parent["selected_endpoints"][key], dtype=np.int64) for key in ("r", "s"))
        R = np.array([json.loads(line) for line in (data / "parent-vectors.jsonl").read_text().splitlines()
                      if line.strip()], dtype=np.int64)
        largest = max(int(np.abs(a).max()) for a in (R, p, r, s))
        self.assertLess(48**2 * (2*largest)**2 * int(np.abs(G).max()), 2**63)
        products_r, products_s = R @ G @ r, R @ G @ s
        vertex = lambda x: frozenset((tuple(x), tuple(p - x)))
        nr = {vertex(x) for x, value in zip(R, products_r) if value in (1, 3)}
        ns = {vertex(x) for x, value in zip(R, products_s) if value in (1, 3)}
        self.assertEqual((len(nr), len(ns), len(nr & ns), len(nr - ns)), (368, 368, 70, 298))
        endpoints = R[(products_r == 3) & (products_s == 2)]
        self.assertEqual({vertex(x) for x in endpoints}, nr - ns)
        witnesses = {tuple(p - x) for x in endpoints}
        saved = json.loads((data / "record.json").read_text())["t_witness_vectors"]
        self.assertEqual(len(witnesses), 298)
        self.assertEqual(witnesses, {tuple(row) for row in saved})

    def test_rational_matrix_identity(self):
        data = json.loads((ROOT / "constructions/sections/d43/data/certificate.json").read_text())
        A = [[Fraction(x) for x in row] for row in data["A_rows"]]
        b, c, w = ([Fraction(x) for x in data[key]] for key in ("b_rhs", "target_c", "dual_w"))
        self.assertEqual([sum(w[i]*A[i][j] for i in range(len(A))) for j in range(len(c))], c)
        self.assertEqual(sum(x*y for x, y in zip(w, b)), 2553792)

    def test_support_region_census(self):
        data = json.loads((ROOT / "research/data/support-regions.json").read_text())
        for expected in data["results"]:
            with self.subTest(dimension=expected["dimension"]):
                self.assertEqual(check_regions(ROOT, expected["dimension"]), expected)
                witness = expected["maximizing_region"]
                region = set(witness["coordinates_1indexed"])
                dimension = expected["dimension"]
                triples = {int(h, 16) for h in witness["support_hex"]}
                outside = [{i + 1 for i, b in enumerate(line.strip()) if b == "1"}
                           for line in (ROOT / expected["input"]).read_text().splitlines()
                           if line.strip() and not line.startswith("#") and int(line, 2) not in triples]
                # Independently enumerate the maximizing region without bitsets or pruning.
                count = sum(all(len(set(candidate) & old) <= 4 for old in outside)
                            for candidate in combinations(sorted(region), 8))
                self.assertEqual(count, expected["maximum_free_supports"])
                self.assertTrue(region <= set(range(1, dimension + 1)))

    def test_invalid_support_family_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "constructions/codes/data/d32_supports_binary.txt"
            path.parent.mkdir(parents=True)
            first = (1 << 8) - 1
            for second in (first, first ^ 1 ^ (1 << 8)):
                path.write_text(f"{first:032b}\n{second:032b}\n")
                with self.assertRaises(ValueError):
                    check_regions(root, 32)

    def test_intermediate_signed_codes(self):
        record = json.loads((ROOT / "research/data/d35-local-codes.json").read_text())
        path = ROOT / record["input"]
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["input_sha256"])
        parent = json.loads(path.read_text())
        region = sum(1 << i for i in record["region_coordinates_0based"])
        self.assertEqual(region.bit_count(), 11)
        deleted = set(record["deleted_support_indices_0based"])
        supports = [int(row, 16) for row in parent["old_supports_hex"]]
        self.assertEqual([i for i, row in enumerate(supports) if row & region == row], sorted(deleted))
        self.assertTrue(all((row & region).bit_count() <= 4 for i, row in enumerate(supports)
                            if i not in deleted))
        self.assertEqual(record["local_search_universe"]["signed_vectors"], 165 * 256)
        for code in record["explicit_local_codes"]:
            rows = [(int(a, 16), int(b, 16)) for a, b in code["signed_vectors_hex"]]
            self.assertEqual(len(rows), len(set(rows)))
            self.assertEqual(len(rows), code["points"])
            self.assertEqual(code["points"] - code["removed_points"], code["gain"])
            for support, negative in rows:
                self.assertEqual(support.bit_count(), 8)
                self.assertEqual(support & region, support)
                self.assertEqual(negative & support, negative)
            for (a, negative_a), (b, negative_b) in combinations(rows, 2):
                overlap = a & b
                self.assertLessEqual(overlap.bit_count() - 2*((negative_a ^ negative_b) & overlap).bit_count(), 4)
        observation = record["affine_search_observation"]
        self.assertEqual([2**d for d in observation["sign_dimension_per_family"]],
                         observation["points_per_family"])
        self.assertEqual(sum(observation["points_per_family"]), observation["points"])


if __name__ == "__main__":
    unittest.main()
