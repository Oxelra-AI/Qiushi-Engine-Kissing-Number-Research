#!/usr/bin/env python3
"""Compile and run the independent C++17 checker on all five certificates."""
import argparse
import json
import os
import subprocess
import time
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def verify():
    start = time.monotonic()
    temporary = tempfile.TemporaryDirectory(prefix='kissing-code-check-')
    build = Path(temporary.name)
    executable = build / 'exact-checker'
    subprocess.run([os.environ.get('CXX', 'c++'), '-std=c++17', '-O2', '-Wall', '-Wextra',
                    str(ROOT / 'independent.cpp'), '-o', str(executable)], check=True)
    results = []
    for c in json.loads((ROOT / 'data/claims.json').read_text()):
        args = [str(c[k]) for k in ('dimension', 'top_length', 'support_size', 'lower_bound', 'top_size')]
        args += [str(ROOT / c[k]) for k in ('kernel_file', 'representatives_file', 'support_file')]
        result = subprocess.run([str(executable), *args], check=True, capture_output=True, text=True)
        results.append(json.loads(result.stdout))
    temporary.cleanup()
    return dict(checker='Independent C++17 integer checker', valid=True, results=results,
                floating_point_used_for_acceptance=False,
                elapsed_seconds=round(time.monotonic() - start, 3))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    text = json.dumps(verify(), indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end='')
