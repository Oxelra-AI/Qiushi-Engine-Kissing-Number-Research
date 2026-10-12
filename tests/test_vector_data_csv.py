from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


@unittest.skipUnless(shutil.which("g++"), "C++ compiler required")
class IntegerCsv(unittest.TestCase):
    def test_default_and_explicit_widths(self):
        source = Path(__file__).resolve().parents[1] / "constructions/sections/vector_data_csv.cpp"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "convert"
            subprocess.run(["g++", "-O2", "-std=c++17", str(source), "-o", str(binary)],
                           check=True, capture_output=True)
            for width in (48, 72):
                values = [i % 25 - 12 for i in range(3 * width)]
                data = root / "points.i8"
                data.write_bytes(bytes(x % 256 for x in values))
                command = [str(binary), str(data)] + ([] if width == 48 else [str(width)])
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                expected = [",".join(map(str, values[i:i + width]))
                            for i in range(0, len(values), width)]
                self.assertEqual(result.stdout.splitlines(), expected)
                data.write_bytes(data.read_bytes()[:-1])
                result = subprocess.run(command, capture_output=True)
                self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
