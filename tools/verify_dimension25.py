#!/usr/bin/env python3
"""Replay the 197580-point proof without modifying the supplied inputs."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys

from package_files import write_json

ROOT = Path(__file__).resolve().parents[1]


def check(data, rejections=False):
    if sys.flags.optimize:
        raise ValueError('Run without -O: verification uses assertions.')
    sys.path.insert(0, str(data.resolve()))
    import verify_baseline
    import verify_extension
    import check_rejections
    verify_baseline.HERE = data.resolve()
    verify_extension.HERE = data.resolve()
    check_rejections.HERE = data.resolve()
    with contextlib.redirect_stdout(io.StringIO()):
        baseline = verify_baseline.main()
        extension = verify_extension.main()
        negative = check_rejections.main() if rejections else []
    return {'passed': bool(baseline['baseline_verified'] and extension['extension_verified']),
            'dimension': 25, 'points': extension['points'], 'baseline': baseline,
            'extension': extension, 'negative_tests': negative,
            'negative_tests_passed': bool(negative) and all(r['rejected'] for r in negative)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT / 'constructions/d25')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rejections', action='store_true')
    args = parser.parse_args()
    result = check(args.data, args.rejections)
    write_json(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
