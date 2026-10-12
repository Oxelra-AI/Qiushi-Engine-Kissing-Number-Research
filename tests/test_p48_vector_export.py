"""Small exhaustive checks of the full-shell indexing and lifting data path."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
P48 = ROOT / "constructions/p48"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INDEX = load("p48_index", P48 / "index_shell.py")
with patch.object(sys, "path", [str(P48)] + sys.path):
    EXPORT = load("p48_export", P48 / "export_vectors.py")


class CanonicalIndex(unittest.TestCase):
    def test_exact_pair_index_and_duplicate_rejection(self):
        for duplicate in (False, True):
            with tempfile.TemporaryDirectory() as directory, patch.object(INDEX, "SHELL_ROWS", 4), contextlib.redirect_stdout(io.StringIO()):
                root = Path(directory)
                vectors = np.zeros((4, 48), dtype=np.int8)
                vectors[0, 0] = 1
                vectors[1] = -vectors[0]
                vectors[2, 0 if duplicate else 1] = 1
                vectors[3] = -vectors[2]
                vectors.tofile(root / "part-0.i8")
                (root / "enumeration.json").write_text(json.dumps({"stopped": False, "rows": 4}))
                if duplicate:
                    with self.assertRaisesRegex(ValueError, "Repeated antipodal"):
                        INDEX.build(root, root / "lines.i8", chunk_pairs=1)
                else:
                    report = INDEX.build(root, root / "lines.i8", chunk_pairs=1)
                    self.assertTrue(report["passed"])
                    self.assertEqual(report["canonical_lines"], 2)


@unittest.skipUnless(shutil.which("g++"), "C++ compiler required")
class NativeModes(unittest.TestCase):
    def test_antipodal_coefficient_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "enumerate"
            compiled = subprocess.run(["/usr/bin/g++", "-O2", "-std=c++17", "-fopenmp",
                            str(ROOT / "constructions/sections/export_vectors_native.cpp"), "-o", str(binary)],
                           capture_output=True, text=True)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            gram = np.eye(48, dtype=int)
            gram[0, 0] = gram[1, 1] = 2
            geometry = {"dimension": 2, "squared_norm": 2, "expected_rows": 4,
                        "coefficient_output": True, "antipodal_output": True,
                        "gram": [[2, 0], [0, 2]], "output_gram": gram.tolist(),
                        "transform": np.eye(48, dtype=int)[:2].tolist(),
                        "components": [{"center": [0, 0], "offset": [0] * 48, "radius_squared": 2}]}
            path = root / "geometry.json"
            path.write_text(json.dumps(geometry))
            subprocess.run([str(binary), str(path), str(root / "output"), "2", "1"], check=True, capture_output=True)
            rows = np.concatenate([np.fromfile(p, dtype=np.int8).reshape(-1, 48)
                                   for p in sorted((root / "output").glob("part-*.i8"))])
            expected = {tuple(sign * np.eye(48, dtype=int)[i]) for i in range(2) for sign in (-1, 1)}
            self.assertEqual(set(map(tuple, rows)), expected)
            self.assertEqual(len(rows), 4)
            # Preserve the existing default Cartesian/affine path used by
            # the 43D and 45D exporters; neither new option is enabled here.
            transform = np.zeros((2, 48), dtype=int)
            transform[0, 0] = 2
            transform[1, 1:3] = 2
            geometry = {"dimension": 2, "squared_norm": 1, "expected_rows": 2,
                        "gram": [[1, 0], [0, 2]], "transform": transform.tolist(),
                        "components": [{"center": ["1/2", 0], "offset": [-1] + [0] * 47,
                                        "radius_squared": "1/4"}]}
            path.write_text(json.dumps(geometry))
            subprocess.run([str(binary), str(path), str(root / "affine"), "2", "1"], check=True, capture_output=True)
            rows = np.concatenate([np.fromfile(p, dtype=np.int8).reshape(-1, 48)
                                   for p in sorted((root / "affine").glob("part-*.i8"))])
            expected = {tuple(sign * np.eye(48, dtype=int)[0]) for sign in (-1, 1)}
            self.assertEqual(set(map(tuple, rows)), expected)
            self.assertEqual(len(rows), 2)


try:
    from sage.all import ZZ, matrix
    HAVE_SAGE = True
except ImportError:
    HAVE_SAGE = False


@unittest.skipUnless(HAVE_SAGE, "SageMath required for exact Cartesian geometry")
class CartesianLift(unittest.TestCase):
    def test_basis_frame_and_tail_counts(self):
        saved = json.loads((P48 / "data/cartesian-basis.json").read_text())
        g = matrix(ZZ, np.load(P48 / "data/p48p_gram.npy").tolist())
        f = matrix(ZZ, saved["orthogonal_frame_F"])
        b = matrix(ZZ, saved["basis_B"])
        self.assertEqual(f * g * f.transpose(), 6 * matrix.identity(ZZ, 48))
        self.assertEqual(b, g * f.transpose())
        basis, scale = EXPORT.load_basis(P48 / "data/cartesian-basis.json")
        self.assertEqual(scale, 24)
        self.assertEqual(basis.shape, (48, 48))
        for dimension in range(49, 56):
            data = EXPORT.prepare_dimension(dimension, scale)
            self.assertTrue(np.all(np.sum(data["tails"] ** 2, axis=1) == 48))
            self.assertEqual(52416000 + 2 * len(data["coefficients"]) + 2 * len(data["tails"]), EXPORT.COUNTS[dimension])

    def test_small_complete_materialization(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            root = Path(directory)
            vectors = np.zeros((4, 48), dtype=np.int8)
            vectors[0, 0] = vectors[2, 1] = 1
            vectors[1], vectors[3] = -vectors[0], -vectors[2]
            vectors.tofile(root / "part-0.i8")
            (root / "enumeration.json").write_text(json.dumps({"stopped": False, "rows": 4}))
            shell = root / "lines.i8"
            with patch.object(INDEX, "SHELL_ROWS", 4):
                INDEX.build(root, shell)
            fixture = {"coefficients": vectors[:1], "tail_indices": np.array([0]),
                       "tails": np.array([[4, 4, 4]]), "assigned_sizes": [1],
                       "tail_name": "A1", "tail_factors": [4, 4, 4]}
            with patch.object(EXPORT, "N_LINES", 2), patch.dict(EXPORT.COUNTS, {49: 8}), patch.object(EXPORT, "prepare_dimension", return_value=fixture):
                EXPORT.export(shell, P48 / "data/cartesian-basis.json", root / "full", [49], chunk_lines=1)
            points = np.fromfile(root / "full/configuration49.i8", dtype=np.int8).reshape(-1, 51).astype(np.int64)
            norms = np.sum(points * points, axis=1)
            self.assertEqual(norms.tolist(), [144, 144, 192, 192, 192, 192, 48, 48])
            self.assertEqual(len(set(map(tuple, points))), 8)
            normalized = points / np.sqrt(norms[:, None])
            products = normalized @ normalized.T
            np.fill_diagonal(products, -1)
            self.assertLessEqual(float(products.max()), 0.5 + 1e-14)


if __name__ == "__main__":
    unittest.main()
