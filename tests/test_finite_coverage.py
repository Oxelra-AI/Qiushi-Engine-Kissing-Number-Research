"""Finite-pool coverage certificates against exhaustive subset averages."""
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
from pathlib import Path
import unittest

SPEC = spec_from_file_location("coverage", Path(__file__).resolve().parents[1]
                              / "constructions/p48/coverage.py")
COVERAGE = module_from_spec(SPEC)
SPEC.loader.exec_module(COVERAGE)


class FiniteCoverage(unittest.TestCase):
    def test_all_small_incidence_tables(self):
        for m in range(1, 5):
            # Exhaust every incidence assignment of three distinguishable points.
            for masks in product(range(1 << m), repeat=3):
                images = [{x for x, mask in enumerate(masks) if mask >> i & 1}
                          for i in range(m)]
                counts = COVERAGE.incidence_counts(images)
                for target in range(m+1):
                    sizes = [len(set().union(*(images[i] for i in subset)))
                             for subset in combinations(range(m), target)]
                    actual_average = Fraction(sum(sizes), len(sizes))
                    result = COVERAGE.select(counts, m, target)
                    self.assertEqual(Fraction(result["expected_union"]), actual_average)
                    actual_union = len(set().union(*(images[i] for i in result["indices"])))
                    self.assertEqual(actual_union, result["union"])
                    self.assertGreaterEqual(actual_union, actual_average)
                    self.assertEqual(len(set(result["indices"])), target)

    def test_empty_and_universal_points(self):
        for images in ([], [set()], [{0}, {0}, {0}], [{0, 1}, {0, 1}, {0, 1}]):
            for target in range(len(images)+1):
                result = COVERAGE.select(COVERAGE.incidence_counts(images), len(images), target)
                self.assertEqual(result["union"], len(set().union(*(images[i] for i in result["indices"]))))

    def test_invalid_masks(self):
        for counts in ({0: 1}, {8: 1}, {1: -1}, {1: 1.5}):
            with self.assertRaises(ValueError):
                COVERAGE.select(counts, 3, 2)

    def test_exchange_gains_and_termination(self):
        images = [{0, 1, 2}, {1, 2, 3}, {2, 4}, {3, 4, 5}, {5, 6}]
        counts = COVERAGE.incidence_counts(images)
        for target in range(6):
            for start in combinations(range(5), target):
                result = COVERAGE.improve(counts, 5, start)
                final = set(result["indices"])
                size = len(set().union(*(images[i] for i in final)))
                self.assertEqual(size, result["union"])
                self.assertGreaterEqual(size, len(set().union(*(images[i] for i in start))))
                for old in final:
                    for new in set(range(5))-final:
                        swapped = final-{old} | {new}
                        self.assertLessEqual(len(set().union(*(images[i] for i in swapped))), size)

    def test_asymmetric_rational_heights_cannot_evade_poles(self):
        # Rational unit-circle points below height 1/2. Both angles are
        # strictly below pi/6, so even asymmetric paired copies conflict.
        points = set()
        for denominator in range(2, 30):
            for numerator in range(1, denominator):
                parameter = Fraction(numerator, denominator)
                height = 2*parameter/(1+parameter*parameter)
                head = (1-parameter*parameter)/(1+parameter*parameter)
                if height <= Fraction(1, 2):
                    points.add((head, height))
        self.assertGreater(len(points), 20)
        for a, h in points:
            self.assertEqual(a*a+h*h, 1)
            for b, k in points:
                self.assertGreater(a*b-h*k, Fraction(1, 2))

    def test_class_assignment_optimum_is_union(self):
        # Enumerate all assignments, including leaving a line unused.
        # This checks the counting reduction, independently of selection.
        classes = [{0, 1, 2}, {1, 3}, {2, 3, 4}]
        for size in range(4):
            for indices in combinations(range(3), size):
                union = set().union(*(classes[i] for i in indices))
                choices = [[None]+[i for i in indices if x in classes[i]]
                           for x in sorted(union)]
                maximum = max((sum(label is not None for label in labels)
                               for labels in product(*choices)), default=0)
                self.assertEqual(maximum, len(union))


if __name__ == "__main__":
    unittest.main()
