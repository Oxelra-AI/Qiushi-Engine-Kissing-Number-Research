"""The complete report cannot overwrite the published report or its attachment."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_reports import build, report_sources
from package_files import sha256, write_manifest
from package_reports import package
from report_editions import prefix, verify_frozen
from supplement import write


class ReportEditions(unittest.TestCase):
    def fixture(self, root):
        data = {'LICENSE': b'License', 'CITATION.cff': b'title: Fixture'}
        for language in ('en', 'zh'):
            for name, content in [('main.tex', b'TeX fixture'), ('refs.bib', b''),
                                  ('main.pdf', b'PDF fixture'), ('certificates.zip', b'Attachment fixture')]:
                data[prefix(language) + '/' + name] = content
                data[prefix(language, 'complete') + '/' + name] = b'Complete ' + content
        records = [{'path': name, 'sha256': hashlib.sha256(content).hexdigest()}
                   for name, content in data.items() if name.startswith(('reports/en/', 'reports/zh/'))]
        data['reports/livestream.json'] = json.dumps({'schema_version': 1, 'files': records}).encode()
        for name, content in data.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        write_manifest(root, data)
        return records

    def test_default_build_preserves_the_published_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            records = self.fixture(root)
            with patch('build_reports.subprocess.run') as compiler:
                self.assertTrue(build(root, 'en')['preserved'])
                compiler.assert_not_called()
            self.assertEqual(verify_frozen(root), tuple(records))

    def test_changed_published_source_is_rejected_before_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / 'reports/en/main.tex').write_text('Changed source')
            with patch('build_reports.subprocess.run') as compiler:
                with self.assertRaisesRegex(ValueError, 'Published report changed'):
                    build(root, 'en')
                compiler.assert_not_called()

    def test_attachment_write_does_not_regenerate_the_old_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            with patch('supplement.archive_bytes') as generate:
                path = write(root, 'zh')
                generate.assert_not_called()
            self.assertEqual(path.read_bytes(), b'Attachment fixture')

    def test_source_archives_have_different_names_and_membership(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            with patch('package_reports.build'):
                first = package(root, 'en')
                complete = package(root, 'en', 'complete')
            self.assertNotEqual(first, complete)
            self.assertTrue(all(name.startswith('reports/en_full/')
                                for name in report_sources(root, 'en', 'complete')))
            verify_frozen(root)

    def test_actual_published_report_identities(self):
        self.assertEqual(len(verify_frozen(ROOT)), 38)

    def test_report_projects_are_siblings(self):
        self.assertEqual(prefix('en'), 'reports/en')
        self.assertEqual(prefix('zh'), 'reports/zh')
        self.assertEqual(prefix('en', 'complete'), 'reports/en_full')
        self.assertEqual(prefix('zh', 'complete'), 'reports/zh_full')
        self.assertFalse((ROOT / 'reports/full').exists())

    def test_invalid_report_paths_are_rejected(self):
        for language, edition in [('../en', 'complete'), ('en', '../complete'), ('fr', 'livestream')]:
            with self.assertRaises(ValueError):
                prefix(language, edition)


if __name__ == '__main__':
    unittest.main()
