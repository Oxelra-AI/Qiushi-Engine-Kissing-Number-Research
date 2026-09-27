#!/usr/bin/env python3
"""Export only the files required to compile the paper."""
import argparse
from pathlib import Path
import re
import zipfile

from package_files import approved_paths, contained_file

ROOT = Path(__file__).resolve().parents[1]


def paper_sources(root):
    """Resolve the manuscript's braced input, include and bibliography commands."""
    approved = set(approved_paths(root))
    selected = set()

    def visit(name):
        path = contained_file(root, name)
        if name not in approved:
            raise ValueError("A paper input is absent from the package manifest: " + name)
        if name in selected:
            return
        selected.add(name)
        if path.suffix != '.tex':
            return
        text = re.sub(r'(?<!\\)%[^\n]*', '', path.read_text())
        for command, group in re.findall(r'\\(input|include|bibliography)\{([^}]+)\}', text):
            suffix = '.bib' if command == 'bibliography' else '.tex'
            names = group.split(',') if command == 'bibliography' else [group]
            for target in names:
                target = target.strip()
                visit('paper/' + (target if Path(target).suffix else target + suffix))
        for target in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text):
            variants = [target] if Path(target).suffix else [
                target + suffix for suffix in ('.pdf', '.png', '.jpg', '.jpeg', '.eps')]
            candidates = [name for name in variants if 'paper/' + name in approved]
            if len(candidates) != 1:
                raise ValueError("Expected one approved paper figure: " + target)
            visit('paper/' + candidates[0])

    visit('paper/main.tex')
    return tuple(sorted(selected))


def package(root):
    root = Path(root).resolve()
    sources = paper_sources(root)
    output = root / 'dist/kissing-number-paper-source.zip'
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(contained_file(root, name), Path(name).relative_to('paper').as_posix())
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    print(package(args.root))


if __name__ == '__main__':
    main()
