"""Independent small-form enumeration and section-coordinate checks."""
from contextlib import redirect_stdout
from fractions import Fraction
import gzip
import importlib.util
import io
from itertools import product
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "section_export", ROOT / "constructions/sections/export_vectors.py")
EXPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXPORT)


class ExactEnumeration(unittest.TestCase):
    def test_against_exhaustive_cubes(self):
        cases = [([[2, 1], [1, 4]], [0, 0]),
                 ([[2, 1], [1, 4]], [Fraction(1, 3), Fraction(-2, 5)]),
                 ([[3, 1, 0], [1, 2, 1], [0, 1, 2]], [0, Fraction(1, 2), 0])]
        for gram, center in cases:
            n = len(gram)
            by_norm = {}
            for row in product(range(-6, 7), repeat=n):
                a = [x - y for x, y in zip(row, center)]
                norm = sum(a[i] * gram[i][j] * a[j] for i in range(n) for j in range(n))
                if norm <= 8:
                    by_norm.setdefault(norm, set()).add(row)
            for norm, expected in by_norm.items():
                actual = list(EXPORT.exact_shell(gram, center, norm))
                self.assertEqual(len(actual), len(set(actual)))
                self.assertEqual(set(actual), expected)

    def test_boundary_and_empty_shells(self):
        self.assertEqual(set(EXPORT.exact_shell([[1]], [Fraction(1, 2)], Fraction(1, 4))), {(0,), (1,)})
        self.assertEqual(list(EXPORT.exact_shell([[1]], [0], 0)), [(0,)])
        self.assertEqual(list(EXPORT.exact_shell([[2]], [0], 1)), [])
        self.assertEqual(list(EXPORT.exact_shell([[1]], [0], -1)), [])
        with self.assertRaises(ValueError):
            list(EXPORT.exact_shell([[0]], [0], 1))

    def test_partial_and_complete_receipts(self):
        geometry = {"dimension": 1, "coordinate_columns": 48, "squared_norm": 4,
                    "maximum_inner_product": 2, "expected_rows": 2,
                    "orthogonal_to_rows": [], "gram": [[1]],
                    "transform": [[1] + [0] * 47],
                    "components": [{"center": [0], "radius_squared": 4,
                                    "offset": [0] * 48}]}
        for limit, max_nodes, rows, complete in [(None, None, 2, True),
                                                (1, None, 1, False),
                                                (None, 1, 0, False)]:
            with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
                path = Path(directory) / "vectors.csv.gz"
                EXPORT.export(geometry, path, limit, max_nodes)
                receipt = json.loads(Path(str(path) + ".json").read_text())
                self.assertEqual(receipt["rows"], rows)
                self.assertEqual(receipt["complete"], complete)
                with gzip.open(path, "rt") as stream:
                    self.assertEqual(sum(1 for _ in stream), rows)
                with self.assertRaises(FileExistsError):
                    EXPORT.export(geometry, path)

    def test_wrong_expected_count_is_not_complete(self):
        geometry = {"dimension": 1, "coordinate_columns": 48, "squared_norm": 4,
                    "maximum_inner_product": 2, "expected_rows": 3,
                    "orthogonal_to_rows": [], "gram": [[1]],
                    "transform": [[1] + [0] * 47],
                    "components": [{"center": [0], "radius_squared": 4,
                                    "offset": [0] * 48}]}
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            path = Path(directory) / "vectors.csv.gz"
            with self.assertRaisesRegex(ValueError, "proved cardinality"):
                EXPORT.export(geometry, path)
            receipt = json.loads(Path(str(path) + ".json").read_text())
            self.assertTrue(receipt["exhausted"])
            self.assertFalse(receipt["complete"])


try:
    from sage.all import ZZ, matrix, vector
    HAVE_SAGE = True
except ImportError:
    HAVE_SAGE = False


@unittest.skipUnless(HAVE_SAGE, "SageMath required for the full section geometry")
class SectionGeometry(unittest.TestCase):
    def test_exact_geometry_and_known_points(self):
        for dimension in (43, 45):
            geometry = EXPORT.prepare(dimension)
            transform = matrix(ZZ, geometry["transform"])
            gram = matrix(ZZ, geometry["gram"])
            orthogonal = matrix(ZZ, geometry["orthogonal_to_rows"])
            self.assertEqual(transform * orthogonal.transpose(), 0)
            self.assertEqual(transform * transform.transpose(),
                             (96 if dimension == 43 else 768) * gram)
            for component in geometry["components"]:
                offset = vector(ZZ, component["offset"])
                self.assertEqual(orthogonal * offset, 0)
                center = vector(component["center"])
                self.assertEqual(center * transform + offset, 0)
            if dimension == 45:
                offset = geometry["components"][2]["offset"]
                self.assertEqual(sum(x * x for x in offset), 4416)


if __name__ == "__main__":
    unittest.main()
