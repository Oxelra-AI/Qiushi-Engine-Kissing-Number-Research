"""Bind successful replay receipts to the copied inputs and executed code."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from reproduce import missing_dependencies


class ReplayBinding(unittest.TestCase):
    def make_fixture(self, temporary, body):
        root = Path(temporary) / "collection"
        (root / "tools").mkdir(parents=True)
        (root / "constructions").mkdir()
        (root / "constructions/value.txt").write_text("7\n")
        (root / "tools/helper.py").write_text("VALUE = 7\n")
        script = "import json, os, sys\nfrom pathlib import Path\n" + textwrap.dedent(body)
        (root / "tools/check_fixture.py").write_text(script)
        plan = {"schema_version": 1, "jobs": [{
            "id": "fixture", "suite": "current", "description": "Replay binding fixture",
            "requirements": [],
            "command": ["{python}", "{tools}/check_fixture.py", "{output}/fixture.json"],
            "receipt": "fixture.json", "checks": {"passed": True, "value": 7}, "timeout": 15,
        }]}
        (root / "tools/replay_plan.json").write_text(json.dumps(plan))
        return root

    def run_fixture(self, root):
        output = root.parent / "output"
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "tools/reproduce.py"),
             "--root", str(root), "--output", str(output)],
            env=dict(os.environ, REPLAY_TEST_ROOT=str(root)),
            capture_output=True, text=True, timeout=30,
        )
        report = json.loads((output / "reproduction.json").read_text())
        return result, report, output

    def test_execution_and_receipt_use_copied_tools_and_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_fixture(temporary, """
                original = Path(os.environ["REPLAY_TEST_ROOT"])
                (original / "tools/helper.py").write_text("VALUE = 99\\n")
                (original / "constructions/value.txt").write_text("99\\n")
                from helper import VALUE
                copied = Path(__file__).resolve().parents[1]
                value = int((copied / "constructions/value.txt").read_text())
                Path(sys.argv[1]).write_text(json.dumps({"passed": VALUE == value == 7, "value": value}))
            """)
            result, report, output = self.run_fixture(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(report["passed"])
            self.assertTrue(report["inputs_unchanged"])
            records = {entry["path"]: entry["sha256"] for entry in report["input_digest"]["files"]}
            for relative, contents in {
                "constructions/value.txt": b"7\n", "tools/helper.py": b"VALUE = 7\n",
                "tools/replay_plan.json": (root / "tools/replay_plan.json").read_bytes(),
                "tools/reproduce.py": (ROOT / "tools/reproduce.py").read_bytes(),
                "tools/package_files.py": (ROOT / "tools/package_files.py").read_bytes(),
                "tools/check_fixture.py": (root / "tools/check_fixture.py").read_bytes(),
            }.items():
                self.assertEqual(records[relative], hashlib.sha256(contents).hexdigest())
            self.assertTrue(all(not Path(relative).is_absolute() for relative in records))
            self.assertEqual(report["versions"].keys(), {"python"})
            self.assertEqual(set(report["checks"][0]), {"id", "exit_code", "passed", "seconds"})
            self.assertNotIn(temporary, json.dumps(report))
            self.assertTrue((output / "logs/fixture.log").is_file())
            self.assertTrue((output / "fixture.json").is_file())

    def test_a_pass_cannot_hide_a_changed_copied_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_fixture(temporary, """
                copied = Path(__file__).resolve().parents[1]
                (copied / "constructions/value.txt").write_text("99\\n")
                Path(sys.argv[1]).write_text(json.dumps({"passed": True, "value": 7}))
            """)
            result, report, _ = self.run_fixture(root)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(report["checks"][0]["passed"])
            self.assertFalse(report["inputs_unchanged"])
            self.assertFalse(report["passed"])

    def test_cpp_dependency_uses_the_configured_compiler(self):
        with patch.dict(os.environ, {"CXX": "clang++"}), \
                patch("reproduce.shutil.which", side_effect=lambda name: name == "clang++") as which:
            self.assertEqual(missing_dependencies({"c++"}), [])
            which.assert_called_once_with("clang++")
        with patch.dict(os.environ, {}, clear=True), \
                patch("reproduce.shutil.which", return_value=None) as which:
            self.assertEqual(missing_dependencies({"c++"}), ["C++ compiler (CXX or c++)"])
            which.assert_called_once_with("c++")


if __name__ == "__main__":
    unittest.main()
