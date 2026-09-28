"""Fixed E8-coordinate counts, exact rank certificates and rejection controls."""
from fractions import Fraction
import importlib.util
from math import prod
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "e8_coordinate_family", ROOT / "constructions/sections/d43/verify_coordinate_family.py")
FAMILY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FAMILY)


def bareiss_determinant(matrix):
    """Independent fraction-free determinant over Z, not modular arithmetic."""
    a = [list(row) for row in matrix]
    sign, previous = 1, 1
    for k in range(len(a)-1):
        pivot = next((i for i in range(k, len(a)) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[pivot], a[k] = a[k], a[pivot]
            sign *= -1
        value = a[k][k]
        for i in range(k+1, len(a)):
            for j in range(k+1, len(a)):
                numerator = a[i][j]*value-a[i][k]*a[k][j]
                assert numerator % previous == 0
                a[i][j] = numerator//previous
            a[i][k] = 0
        previous = value
    return sign*a[-1][-1]


class E8CoordinateSections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = FAMILY.check()
        cls.domain = FAMILY.DOMAIN.admissible_domain()
        cls.roots = {tuple(3*x for x in r) for r in FAMILY.DOMAIN.root_set()}
        cls.systems = {k: FAMILY.system(cls.domain, cls.roots, k) for k in range(1, 9)}

    def test_all_eight_fixed_counts_and_full_domain(self):
        self.assertTrue(self.report["passed"])
        self.assertEqual(self.report["cut_count"], 8)
        self.assertEqual(self.report["nonexceptional_domain_size"], 26401)
        self.assertEqual(self.report["exceptional_domain_size"], 240)
        counts = [16815624, 10663920, 6688960, 4149504, 2553792, 1593664, 1110360, 1092000]
        ranks = [25, 34, 39, 41, 39, 34, 25, 13]
        for k, count, rank in zip(range(1, 9), counts, ranks):
            row = self.report["families"][k]
            self.assertEqual(row["fixed_coordinate_section_count"], count)
            self.assertEqual(row["full_column_rank"], rank)
            self.assertEqual(row["moment_matrix_shape"][1], rank)
            self.assertEqual(FAMILY.coordinate_count(8-k), count)
        self.assertEqual(self.report["families"][1]["subsystem"], "coordinate axis")

    def test_every_rank_minor_by_independent_integer_determinant(self):
        for k in range(1, 9):
            _, _, matrix, _, _ = self.systems[k]
            rows, expected = FAMILY.RANK_CERTIFICATES[k]
            determinant = bareiss_determinant([matrix[i] for i in rows])
            self.assertNotEqual(determinant, 0)
            self.assertEqual(determinant % FAMILY.PRIME, expected)

    def test_orbit_masses_against_block_radial_sphere_moments(self):
        # Independently integrate the squared norm of a k-dimensional projection.
        for k in range(1, 9):
            groups, _, _, _, masses = self.systems[k]
            for degree in range(6):
                computed = sum(mass*sum(x*x for x in group[0][:k])**degree
                               for group, mass in zip(groups, masses))
                computed += sum(sum(x*x for x in u[:k])**degree for u in self.roots)
                expected = Fraction(52416000*72**degree*prod(k+2*j for j in range(degree)),
                                    prod(48+2*j for j in range(degree)))
                self.assertEqual(computed, expected)

    def test_radial_moments_alone_do_not_identify_the_fixed_child(self):
        groups, _, matrix, rhs, masses = self.systems[5]
        inside = next(i for i, group in enumerate(groups)
                      if sum(x*x for x in group[0]) == 8 and not any(group[0][:5]))
        outside = next(i for i, group in enumerate(groups)
                       if sum(x*x for x in group[0]) == 8 and any(group[0][:5]))
        direction = [0]*len(groups)
        direction[inside], direction[outside] = 1, -1
        for degree in range(6):
            self.assertEqual(sum(change*sum(x*x for x in group[0])**degree
                                 for change, group in zip(direction, groups)), 0)
        self.assertEqual(sum(change for change, group in zip(direction, groups)
                             if not any(group[0][:5])), 1)
        perturbed = [mass+change for mass, change in zip(masses, direction)]
        self.assertTrue(all(mass >= 0 for mass in perturbed))
        with self.assertRaisesRegex(ValueError, "exact moment"):
            FAMILY.check_moments(matrix, rhs, perturbed)

    def test_corrupted_rank_and_moment_data_are_rejected(self):
        _, _, matrix, rhs, masses = self.systems[4]
        rows, residue = FAMILY.RANK_CERTIFICATES[4]
        corrupted = [list(row) for row in matrix]
        for row in corrupted:
            row[1] = row[0]
        with self.assertRaisesRegex(ValueError, "Rank minor certificate"):
            FAMILY.check_rank(corrupted, rows, residue)
        with self.assertRaisesRegex(ValueError, "Rank minor certificate"):
            FAMILY.check_rank(matrix, rows, (residue+1) % FAMILY.PRIME)
        altered_rhs = list(rhs)
        altered_rhs[0] += 1
        with self.assertRaisesRegex(ValueError, "exact moment"):
            FAMILY.check_moments(matrix, altered_rhs, masses)
        altered_matrix = [list(row) for row in matrix]
        altered_matrix[0][0] += 1
        with self.assertRaisesRegex(ValueError, "exact moment"):
            FAMILY.check_moments(altered_matrix, rhs, masses)
        with self.assertRaisesRegex(ValueError, "11-design degree"):
            FAMILY.moment(4, ((6,), ()))

    def test_weyl_correspondence_preserves_the_specified_target_on_the_full_domain(self):
        simple = FAMILY.DOMAIN.simple_roots()
        for u in self.domain | self.roots:
            original = all(FAMILY.DOMAIN.dot(u, r) == 0 for r in simple[:5])
            coordinate = not any(FAMILY.coordinate_weyl_map(u)[:5])
            self.assertEqual(original, coordinate)
        with self.assertRaisesRegex(ValueError, "Weyl reflection word"):
            FAMILY.check_weyl_map(FAMILY.WEYL_WORD[:-1])


if __name__ == "__main__":
    unittest.main()
