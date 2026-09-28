"""Exact section moments, signature refinement and certificate rejection."""
from collections import defaultdict
from fractions import Fraction
import importlib.util
from itertools import permutations
import json
from math import factorial, prod
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "section_statistics", ROOT / "constructions/sections/d45/verify_statistics.py")
STATISTICS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STATISTICS)


class SectionStatistics(unittest.TestCase):
    def test_norm_eight_refinement_excludes_exactly_two_permutation_classes(self):
        domain, exceptional = STATISTICS.signature_domain()
        removed = {y + (-sum(y),) for y in domain
                   if not STATISTICS.norm_eight_admissible(y)}
        expected = set(permutations((3, 3, -3, -3)))
        expected.update(permutations((3, 2, -3, -2)))
        self.assertEqual(removed, expected)
        self.assertEqual(len(removed), 30)
        self.assertTrue(all(STATISTICS.norm_eight_admissible(y) for y in exceptional))
        self.assertIn((3, 3, -3), domain)
        self.assertFalse(STATISTICS.norm_eight_admissible((3, 3, -3)))

    def test_wick_moments_against_quadratic_polynomial_coefficients(self):
        # Expand (z^T H z)^m independently of the checker's pairing recursion.
        terms = {}
        for i in range(3):
            for j in range(i, 3):
                exponent = [0, 0, 0]
                exponent[i] += 1
                exponent[j] += 1
                terms[tuple(exponent)] = STATISTICS.H[i][j] * (1 if i == j else 2)
        polynomial = {(0, 0, 0): 1}
        for m in range(6):
            for alpha, coefficient in polynomial.items():
                numerator = (52416000 * 6**m * coefficient
                             * prod(factorial(a) for a in alpha))
                denominator = (2**m * factorial(m)
                               * prod(48 + 2*j for j in range(m)))
                self.assertEqual(STATISTICS.shell_moment(alpha, STATISTICS.H),
                                 Fraction(numerator, denominator))
            updated = defaultdict(int)
            for alpha, coefficient in polynomial.items():
                for beta, factor in terms.items():
                    updated[tuple(a+b for a, b in zip(alpha, beta))] += coefficient * factor
            polynomial = dict(updated)

    def test_exact_count_identity_and_universal_anchor_moments(self):
        result = STATISTICS.check()
        self.assertTrue(result["passed"])
        self.assertEqual((result["refined_signatures"], result["refined_free_orbits"]),
                         (209, 101))
        self.assertEqual(result["exact_constant"], 7377408)
        self.assertEqual((result["anchor_endpoint_count"], result["anchor_second_moment"],
                          result["anchor_degree"]), (2256, 768, 368))
        self.assertEqual(len(result["excluded_positive_slacks"]), 7)

    def test_corrupted_multiplier_is_rejected(self):
        saved = json.loads((STATISTICS.DATA / "dual.json").read_text())
        index = next(i for i, value in enumerate(saved["dual"]) if Fraction(value))
        saved["dual"][index] = str(Fraction(saved["dual"][index]) + 1)
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            (data / "dual.json").write_text(json.dumps(saved))
            with self.assertRaisesRegex(ValueError, "Original rational lower certificate"):
                STATISTICS.check(data)

    def test_reordered_signatures_are_rejected(self):
        saved = json.loads((STATISTICS.DATA / "dual.json").read_text())
        saved["signature_representatives"].reverse()
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            (data / "dual.json").write_text(json.dumps(saved))
            with self.assertRaisesRegex(ValueError, "Signature ordering"):
                STATISTICS.check(data)


if __name__ == "__main__":
    unittest.main()
