"""Independent exact point checks, including adversarial binary inputs."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VERIFY = load("section_binary", "constructions/sections/verify_vector_binary.py")


class BinaryChecks(unittest.TestCase):
    def setUp(self):
        self.checks = {
            "dimension": 43, "squared_norm": 1, "expected_rows": 2, "modulus": 96,
            "inverse_scaled": (96 * np.eye(48, dtype=np.int64)).tolist(),
            "orthogonal_to_rows": [[0, 1] + [0] * 46], "residues": [[0] * 48],
        }
        self.points = np.zeros((2, 48), dtype=np.int8)
        self.points[:, 0] = [1, -1]

    def report(self, points, checks=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "points.i8"
            points.tofile(path)
            return VERIFY.verify(path, checks or self.checks, chunk_rows=1)

    def test_complete_synthetic_and_chunking(self):
        report = self.report(self.points)
        self.assertTrue(report["passed"])
        self.assertEqual(report["unique_rows"], 2)
        self.assertEqual(report["integer_arithmetic"], "int32")
        self.assertFalse(report["pairwise_inner_products_checked"])

    def test_partial_and_empty_are_not_complete(self):
        for points in (self.points[:1], self.points[:0]):
            report = self.report(points)
            self.assertFalse(report["passed"])
            self.assertFalse(report["checks"]["expected_row_count"])

    def test_duplicate_invalid_norm_and_nonorthogonal(self):
        duplicate = self.points.copy()
        duplicate[1] = duplicate[0]
        self.assertFalse(self.report(duplicate)["checks"]["all_unique"])
        invalid = self.points.copy()
        invalid[1, 0] = -128
        self.assertEqual(self.report(invalid)["invalid_norm_rows"], 1)
        invalid[1] = 0
        invalid[1, 1] = 1
        report = self.report(invalid)
        self.assertEqual(report["nonorthogonal_rows"], 1)
        self.assertTrue(report["checks"]["all_squared_norms"])

    def test_invalid_membership_and_truncated_row(self):
        checks = dict(self.checks, inverse_scaled=np.eye(48, dtype=np.int64).tolist())
        self.assertEqual(self.report(self.points, checks)["invalid_membership_rows"], 2)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.i8"
            path.write_bytes(b"x" * 47)
            with self.assertRaisesRegex(ValueError, "48-byte rows"):
                VERIFY.verify(path, self.checks)

    def test_integer_overflow_bounds(self):
        self.assertEqual(VERIFY.arithmetic_dtype([[2 ** 24]], [[0]]), np.dtype("int64"))
        with self.assertRaisesRegex(ValueError, "exceed int64"):
            VERIFY.arithmetic_dtype([[2 ** 63]], [[0]])


try:
    from sage.all import QQ, ZZ, matrix, vector
    HAVE_SAGE = True
except ImportError:
    HAVE_SAGE = False


@unittest.skipUnless(HAVE_SAGE, "SageMath required for exact section checks")
class ExactSectionChecks(unittest.TestCase):
    def test_inverse_checks_and_positive_fibre(self):
        for dimension in (43, 45):
            checks = VERIFY.prepare_checks(dimension)
            self.assertEqual(VERIFY.arithmetic_dtype(checks["inverse_scaled"], checks["orthogonal_to_rows"]),
                             np.dtype("int32"))
        data = ROOT / "constructions/sections/d45/data"
        compact = json.loads((data / "compact.json").read_text())
        b = matrix(ZZ, json.loads((data / "parent.json").read_text())["basis_scaled_by_sqrt12"])
        t = matrix(ZZ, compact["section_basis_T_rows"])
        w = vector(ZZ, compact["projection_witness_rows_W"][2])
        point = (8 * w - vector(ZZ, [1, 1, 2]) * t) * b
        points = np.asarray([list(point), list(-point)], dtype=np.int8)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "points.i8"
            points.tofile(path)
            report = VERIFY.verify(path, checks, chunk_rows=1)
        self.assertTrue(report["checks"]["all_squared_norms"])
        self.assertTrue(report["checks"]["all_orthogonal"])
        self.assertEqual(report["fibre_rows"], [0, 0, 1])
        self.assertEqual(report["invalid_membership_rows"], 1)
        self.assertFalse(report["passed"])

    def test_individual_fibre_count_identity(self):
        moments = load("section_moments", "constructions/sections/d45/verify_statistics.py")
        _, _, free, _, rows, rhs, _ = moments.reconstruct()
        active = [j for j, y in enumerate(free) if moments.norm_eight_admissible(y)]
        signatures = [free[j] for j in active]
        a = matrix(QQ, [[row[j] for j in active] for row in rows])
        b = vector(QQ, rhs)
        witness = moments.canonical((-2, -2, 3))
        for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            c = vector(QQ, [int(y == moments.canonical(e)) - 3 * int(y == witness)
                            for y in signatures])
            dual = a.transpose().solve_right(c)
            self.assertEqual(a.transpose() * dual, c)
            self.assertEqual(dual * b, 2459136)
            self.assertEqual(dual * b + 3 * 298, VERIFY.FIBRE_ROWS)


if __name__ == "__main__":
    unittest.main()
