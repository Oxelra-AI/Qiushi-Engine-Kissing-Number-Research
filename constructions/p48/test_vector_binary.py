"""Small source-exact integration test; run with Sage's Python."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import export_vectors as exporter
import verify_vector_binary as checker


class VectorBinaryTest(unittest.TestCase):
    def test_source_reconstruction_and_corruption(self):
        c = np.load(checker.ROOT / "data/class_p48_7077.npy").astype(np.int64)
        selected = set(map(bytes, checker.canonical(c).astype(np.int8)))
        self.assertEqual(len(selected), 7077)
        extras = set()
        matrices = np.load(checker.ROOT / "data/dim50_group_elems.npy").astype(np.int64)
        for a in matrices:
            for row in checker.canonical(c @ a).astype(np.int8):
                key = bytes(row)
                if key not in selected:
                    extras.add(key)
                    if len(extras) == 3:
                        break
            if len(extras) == 3:
                break
        self.assertEqual(len(extras), 3)
        keys = sorted(selected | extras)
        rows = 2 * len(keys) + 2 * len(selected) + 2
        with tempfile.TemporaryDirectory() as temporary, contextlib.ExitStack() as stack:
            directory = Path(temporary)
            shell = directory / "shell.i8"
            shell.write_bytes(b"".join(keys))
            shell.with_name(shell.name + ".json").write_text(json.dumps({
                "passed": True, "canonical_lines": len(keys), "all_lines_distinct": True,
                "sha256": checker.sha256(shell)}))
            for module in (exporter, checker):
                stack.enter_context(patch.object(module, "N_LINES", len(keys)))
                stack.enter_context(patch.dict(module.COUNTS, {49: rows}))
            basis = exporter.ROOT / "data/cartesian-basis.json"
            with contextlib.redirect_stdout(io.StringIO()):
                exporter.export(shell, basis, directory, dimensions=[49], chunk_lines=7)
                result = checker.verify(shell, basis, directory, dimensions=[49], chunk_lines=23)
            self.assertTrue(result["passed"])
            record = result["results"][0]
            self.assertEqual((record["rows"], record["exact_rank"]), (28316, 49))
            self.assertEqual((record["equatorial_rows"], record["cap_rows"], record["pure_tail_rows"]),
                             (6, 28308, 2))

            metadata_path = directory / "configuration49.json"
            original_metadata = metadata_path.read_text()
            metadata = json.loads(original_metadata)
            metadata["blocks"][1]["squared_norm"] = 144
            metadata_path.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError, "row-block or normalization"):
                checker.verify(shell, basis, directory, dimensions=[49])
            metadata_path.write_text(original_metadata)

            binary = directory / "configuration49.i8"
            damaged = bytearray(binary.read_bytes())
            damaged[0] ^= 1
            binary.write_bytes(damaged)
            with self.assertRaisesRegex(ValueError, "Source reconstruction mismatch"):
                checker.verify(shell, basis, directory, dimensions=[49])


if __name__ == "__main__":
    unittest.main()
