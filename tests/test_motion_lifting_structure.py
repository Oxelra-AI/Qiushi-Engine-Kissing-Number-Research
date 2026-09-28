"""Focused exact checks of chord-boundary and reuse refinements."""
from fractions import Fraction
import importlib.util
from itertools import combinations, product
from pathlib import Path
import sys
import unittest

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]


def module(relative, name):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(value)
    finally:
        sys.path.remove(str(path.parent))
    return value


def boundary_minimum(rows):
    """Unit-circle test for rational (A, B, mandatory, cost) data."""
    candidates = [(sp.Integer(1), sp.Integer(0))]
    for (a, b), bound, _, _ in rows:
        a, b, bound = map(sp.Rational, (a, b, bound))
        norm = a*a+b*b
        if norm and bound*bound <= norm:
            radical = sp.sqrt(norm-bound*bound)
            candidates.extend(((bound*a-sign*radical*b)/norm,
                               (bound*b+sign*radical*a)/norm) for sign in (-1, 1))
    costs = []
    for x, y in candidates:
        if sp.simplify(x*x+y*y) != 1:
            raise AssertionError('Boundary candidate left the circle')
        failures = [row for row in rows
                    if bool(sp.simplify(row[0][0]*x+row[0][1]*y-row[1]) > 0)]
        if not any(row[2] for row in failures):
            costs.append(sum(row[3] for row in failures))
    return min(costs) if costs else None


class MotionLiftingStructure(unittest.TestCase):
    def test_exact_boundary_candidates(self):
        h = lambda a, b, bound: ((a, b), sp.Rational(bound), True, 0)
        s = lambda a, b, bound, cost: ((a, b), sp.Rational(bound), False, cost)
        cases = [([], 0), ([h(0, 0, -1)], None),
                 ([h(1, 0, 0), h(-1, 0, 0)], 0),
                 ([h(1, 0, '-3/4'), h(-1, 0, '-3/4')], None),
                 ([h(a, b, '1/2') for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))], None),
                 ([s(1, 0, 0, 3), s(-1, 0, 0, 5)], 0),
                 ([h(-1, 0, '-3/4'), s(1, 0, 0, 4)], 4),
                 ([h(1, 0, 0), h(0, 1, 0), s(-1, 0, 0, 2), s(0, -1, 0, 3)], 2),
                 ([h(1, 0, -1), s(0, 1, '-1/2', 7)], 7),
                 ([s(0, 0, -1, 6)], 6), ([h(1, 0, 2)], 0)]
        for rows, expected in cases:
            with self.subTest(rows=rows):
                self.assertEqual(boundary_minimum(rows), expected)

    def test_dimension_and_latitude_sharpness(self):
        for k in range(1, 6):
            for h2 in map(Fraction, ('1/10', '1/4', '1/3', '3/8', '2/5', '49/100')):
                r = min(k+1, int(1/(1-2*h2)))
                self.assertGreaterEqual(r, 1)
                if r > 1:
                    self.assertLessEqual(r-1, k)
                    self.assertLessEqual(-h2/(r-1), h2-Fraction(1, 2))
                    self.assertEqual(h2+(r-1)*(-h2/(r-1)), 0)
        for r in range(2, 9):
            h2 = Fraction(r-1, 2*r)
            self.assertEqual((Fraction(1, 2)-h2)/(1-h2), Fraction(1, r+1))
            self.assertEqual(1-h2-h2/(r-1), Fraction(1, 2))

    def test_low_latitude_hypothesis_is_essential(self):
        # An antipodal base block admits five pentagonal tails in dimension two
        # at h^2=3/4; the low-latitude dimension bound would be false here.
        h2 = sp.Rational(3, 4)
        self.assertEqual(-(1-h2)+h2, sp.Rational(1, 2))
        self.assertTrue(1-h2+h2*(sp.sqrt(5)-1)/4 < sp.Rational(1, 2))
        self.assertLess(2, 5-1)

    def test_actual_motion_obstructions(self):
        result = module('constructions/d25/verify_motion_obstructions.py',
                        'motion_obstructions_test').check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['minimum_cap_changes'], 2)

    def test_all_144_endpoint_contact_layers(self):
        result = module('constructions/d38/verify_contacts.py',
                        'endpoint_contacts_test').check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['checked_lines'], 144)
        self.assertEqual(result['total_new_point_old_cap_contacts'], 476928)
        obstruction = result['norm64_obstruction']
        self.assertEqual(obstruction['positive_extreme_heads'], 46)
        self.assertEqual(obstruction['negative_extreme_heads'], 46)
        self.assertEqual(obstruction['old_cap_conflicts_per_endpoint'], 138)

    def test_minimum_does_not_control_two_added_shells(self):
        for m, b, c in ((1, 2, 3), (2, 4, 6), (32, 48, 64),
                        (Fraction(3, 2), 2, Fraction(7, 2))):
            m, b, c = map(Fraction, (m, b, c))
            cross = (b-c+m)/2
            self.assertLessEqual(abs(cross), m/2)
            self.assertGreater(m*b-cross*cross, 0)
            for a, n in product(range(-5, 6), repeat=2):
                if a or n:
                    norm = m*a*a+2*cross*a*n+b*n*n
                    self.assertGreaterEqual(norm, m*(a*a-abs(a*n)+n*n))
                    self.assertGreaterEqual(norm, m)
            dot = b-cross
            self.assertEqual(b+m-2*cross, c)
            self.assertGreater(4*dot*dot, b*c)

    def test_orthogonal_multi_shell_example(self):
        # Z^5, m=1, q=3: two norm-two and four norm-three lines.
        vectors = [(1, s, 0, 0, 0) for s in (-1, 1)]
        vectors += [(0, 0, 1, s, t) for s, t in product((-1, 1), repeat=2)]
        dot = lambda a, b: sum(x*y for x, y in zip(a, b))
        for v, w in combinations(vectors, 2):
            b, c = dot(v, v), dot(w, w)
            self.assertLessEqual(4*dot(v, w)**2, b*c)
            self.assertEqual(min(dot(tuple(x-y for x, y in zip(v, w)),
                                         tuple(x-y for x, y in zip(v, w))),
                                 dot(tuple(x+y for x, y in zip(v, w)),
                                     tuple(x+y for x, y in zip(v, w)))),
                             b+c-2*abs(dot(v, w)))
        for v in vectors:
            b = dot(v, v)
            self.assertIn(b, (2, 3))
            self.assertTrue(all(4*x*x <= b*3 for x in v))


if __name__ == '__main__':
    unittest.main()
