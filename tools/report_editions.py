"""Stable locations and identities of the published and complete reports."""
import json

from package_files import approved_paths, contained_file, sha256


def prefix(language, edition='livestream'):
    if language not in ('en', 'zh') or edition not in ('livestream', 'complete'):
        raise ValueError('Unknown report language or edition')
    return 'reports/' + language + ('_full' if edition == 'complete' else '')


def frozen_records(root):
    if 'reports/livestream.json' not in approved_paths(root):
        return ()
    record = json.loads(contained_file(root, 'reports/livestream.json').read_text())
    if record.get('schema_version') != 1:
        raise ValueError('Unknown published-report record')
    entries = record['files']
    names = [entry['path'] for entry in entries]
    if len(names) != len(set(names)) or any(
            not name.startswith(('reports/en/', 'reports/zh/')) for name in names):
        raise ValueError('Invalid published-report file list')
    return tuple(entries)


def verify_frozen(root):
    entries = frozen_records(root)
    approved = set(approved_paths(root))
    for entry in entries:
        name = entry['path']
        if name not in approved or sha256(contained_file(root, name)) != entry['sha256']:
            raise ValueError('Published report changed: ' + name)
    return entries
