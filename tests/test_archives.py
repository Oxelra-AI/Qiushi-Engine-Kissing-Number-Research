"""Only explicitly listed sources belong to downloadable archives."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_reports import report_sources
from package_files import approved_paths, contained_file, write_manifest
from package_reports import package
from supplement import contents


class ArchiveMembership(unittest.TestCase):
    def fixture(self, root):
        data = {"LICENSE": "License\n", "RIGHTS.md": "Rights\n", "CITATION.cff": "title: Example\n",
                "requirements.txt": "", "tools/package_files.py": "", "tools/reproduce.py": "",
                "tools/check_package.py": "", "tools/replay_plan.json": '{"jobs": []}',
                "constructions/catalog/results.json": '{"results": []}',
                "constructions/finite.txt": "1 2 3\n", "reports/en/main.tex": "Report\n",
                "reports/en/refs.bib": "", "reports/en/main.pdf": "PDF fixture\n",
                "reports/en/certificates.zip": "Attachment fixture\n"}
        for name, text in data.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        write_manifest(root, data)
        return set(data)

    def add_extras(self, root):
        for name in (".env", "private/note.md", "constructions/.env",
                     "constructions/private/note.md", "constructions/unlisted.txt",
                     "reports/en/draft.tex", "reports/en/unpublished.pdf",
                     "reports/en/figures/unlisted.png", "reports/en/private/note.tex"):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Unlisted fixture, not for the archive.\n")

    def test_supplement_excludes_unlisted_and_ignored_files_without_git(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            expected = contents(root)
            self.add_extras(root)
            self.assertEqual(contents(root), expected)
            self.assertFalse((root / ".git").exists())

    def test_report_archive_excludes_drafts_and_unlisted_images(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            expected = report_sources(root, "en")
            self.add_extras(root)
            self.assertEqual(report_sources(root, "en"), expected)
            with patch("package_reports.build"):
                archive = package(root, "en")
            with zipfile.ZipFile(archive) as bundle:
                self.assertEqual(set(bundle.namelist()), {
                    "main.tex", "refs.bib", "main.pdf", "certificates.zip",
                    "README.md", "LICENSE", "CITATION.cff"})

    def test_hash_refresh_preserves_membership(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected = self.fixture(root)
            self.add_extras(root)
            subprocess.run([sys.executable, "-B", str(ROOT / "tools/make_manifest.py"),
                            "--root", str(root)], check=True, capture_output=True)
            self.assertEqual(set(approved_paths(root)), expected)

    def test_missing_manifest_is_not_replaced_by_directory_discovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "unlisted.txt").write_text("Not a package\n")
            with self.assertRaises(FileNotFoundError):
                contents(root)

    def test_unlisted_verifier_is_not_added_by_a_replay_command(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / "tools/replay_plan.json").write_text(json.dumps({"jobs": [
                {"command": ["{tools}/unlisted.py"]}]}))
            (root / "tools/unlisted.py").write_text("pass\n")
            with self.assertRaisesRegex(ValueError, "absent"):
                contents(root)

    def test_duplicate_or_escaping_manifest_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for names in (("a", "a"), ("../a",), ("/a",), ("a/../b",),
                          ("a//b",), ("a\\b",), ("manifest.json",)):
                (root / "manifest.json").write_text(json.dumps({"schema_version": 1,
                    "files": [{"path": name} for name in names]}))
                with self.assertRaises(ValueError):
                    approved_paths(root)

    def test_linked_parent_directory_is_rejected_even_inside_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "actual").mkdir()
            (root / "actual/finite.txt").write_text("1 2 3\n")
            (root / "linked").symlink_to(root / "actual", target_is_directory=True)
            with self.assertRaises(ValueError):
                contained_file(root, "linked/finite.txt")


if __name__ == "__main__":
    unittest.main()
