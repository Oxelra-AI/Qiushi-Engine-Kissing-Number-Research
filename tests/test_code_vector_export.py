"""Focused exact geometry and corruption checks for integer ERS exports."""
import gzip
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from constructions.codes import export_vectors as export


class IntegerCodeExports(unittest.TestCase):
    def test_all_final_cardinalities_and_source_checks(self):
        for dimension, count in export.EXPECTED.items():
            spec = export.prepare(dimension)
            rows = export.generate(spec)
            result = export.verify(rows, spec)
            self.assertEqual(rows.shape, (count, dimension))
            self.assertTrue(result["passed"])
            self.assertEqual(result["unique_rows"], count)
            if dimension == 39:
                self.assertEqual(result["squared_norm_counts"], {"32": 435988, "39": 327680})
            else:
                self.assertEqual(result["squared_norm_counts"], {"32": count})

    def test_rejects_invalid_members_duplicate_and_partial(self):
        spec = export.prepare(32)
        rows = export.generate(spec)
        with self.assertRaisesRegex(ValueError, "shape"):
            export.verify(rows[:-1], spec)
        duplicate = rows.copy()
        duplicate[-1] = duplicate[-2]
        with self.assertRaisesRegex(ValueError, "Repeated"):
            export.verify(duplicate, spec)
        invalid = rows.copy()
        invalid[0, 0] *= -1  # minimum sign-code distance is eight
        with self.assertRaisesRegex(ValueError, "not a member"):
            export.verify(invalid, spec)
        invalid = rows.copy()
        first_middle = len(spec["top_words"])
        column = np.flatnonzero(invalid[first_middle])[0]
        invalid[first_middle, column] *= -1  # breaks retained even parity
        with self.assertRaisesRegex(ValueError, "not a member"):
            export.verify(invalid, spec)

    def test_binary_roundtrip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            report = export.export(32, directory)
            target = Path(directory) / "configuration32.i8.gz"
            with gzip.open(target, "rb") as stream:
                rows = np.frombuffer(stream.read(), dtype=np.int8).reshape(-1, 32)
            self.assertEqual(len(rows), 347584)
            saved = json.loads((Path(directory) / "configuration32.json").read_text())
            self.assertEqual(saved, report)
            with self.assertRaises(FileExistsError):
                export.export(32, directory)


if __name__ == "__main__":
    unittest.main()
