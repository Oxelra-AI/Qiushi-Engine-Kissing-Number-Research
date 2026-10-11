"""Exact invariance tests for the optional fast-enumeration basis preparation."""
import json
import unittest

from constructions.sections.export_vectors import prepare
from constructions.sections.prepare_fast import prepare_reduced

try:
    import fpylll
    from sage.all import QQ, ZZ, matrix, vector
    HAVE_BACKEND = True
except ImportError:
    HAVE_BACKEND = False


@unittest.skipUnless(HAVE_BACKEND, "SageMath and fpylll are required")
class ReducedBasisGeometry(unittest.TestCase):
    def test_integral_geometry_and_affine_equations(self):
        for dimension in (43, 45):
            original = prepare(dimension)
            reduced = prepare_reduced(dimension)
            u = matrix(ZZ, reduced["basis_preparation"]["basis_change_U"])
            q = matrix(ZZ, original["gram"])
            new_q = matrix(ZZ, reduced["gram"])
            t = matrix(ZZ, original["transform"])
            new_t = matrix(ZZ, reduced["transform"])
            self.assertEqual(abs(u.det()), 1)
            self.assertEqual(new_q, u * q * u.transpose())
            self.assertEqual(new_t, u * t)
            for key in ("dimension", "coordinate_columns", "squared_norm",
                        "maximum_inner_product", "expected_rows", "orthogonal_to_rows"):
                self.assertEqual(reduced[key], original[key])
            for old, new in zip(original["components"], reduced["components"]):
                c = vector(QQ, [str(x) for x in old["center"]])
                new_c = vector(QQ, [str(x) for x in new["center"]])
                self.assertEqual(new_c * u, c)
                self.assertEqual(new["offset"], old["offset"])
                self.assertEqual(new["radius_squared"], old["radius_squared"])
                a = vector(ZZ, [i % 3 - 1 for i in range(dimension)])
                old_a = a * u
                self.assertEqual(a * new_t, old_a * t)
                self.assertEqual((a - new_c) * new_q * (a - new_c),
                                 (old_a - c) * q * (old_a - c))
            # The native enumerator reads exact rational values as strings.
            saved = json.loads(json.dumps(reduced, default=str))
            for component in saved["components"]:
                self.assertIsInstance(component["radius_squared"], str)
                self.assertTrue(all(isinstance(x, str) for x in component["center"]))

    def test_invalid_iteration_parameters(self):
        with self.assertRaisesRegex(ValueError, "loops must be positive"):
            prepare_reduced(43, loops=0)
        with self.assertRaisesRegex(ValueError, "block size"):
            prepare_reduced(43, blocks=(44,))


if __name__ == "__main__":
    unittest.main()
