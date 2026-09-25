#!/usr/bin/env python3
"""Verify all five exact code certificates; failures have nonzero exit status."""
import argparse
import json
import math
import time
from pathlib import Path
import reference_checker as checker

ROOT = Path(__file__).resolve().parent


def verify(root=ROOT):
    start = time.monotonic()
    results = []
    for claim in json.loads((root / 'data/claims.json').read_text()):
        n, n0 = claim['dimension'], claim['top_length']
        if not 32 <= n0 <= n <= 63:
            raise ValueError('Invalid dimension or top length')
        top = checker.verify_top(n0, root / claim['kernel_file'], root / claim['representatives_file'])
        support = checker.verify_support(n, root / claim['support_file'])
        geometry = checker.geometry_checks(n, n0, top['top_min_distance'], support['valid_support_code'])
        total = top['top_size'] + 128 * support['size'] + 4 * math.comb(n, 2)
        if not (top['valid_top_sign_code'] and support['valid_support_code']
                and all(c['ok'] for c in geometry) and total == claim['lower_bound']
                and top['top_size'] == claim['top_size'] and support['size'] == claim['support_size']):
            raise ValueError(f'Certificate rejected for dimension {n}')
        for obj in (top, support):
            for key, value in list(obj.items()):
                if key.endswith('_file'):
                    obj[key] = Path(value).relative_to(root).as_posix()
        results.append(dict(dimension=n, lower_bound=total, valid=True, top=top,
                            support=support, geometry_checks=geometry))
    if [r['dimension'] for r in results] != [33, 34, 37, 38, 39]:
        raise ValueError('Unexpected claim set')
    return dict(checker='Python exact code and layer checker', valid=True, results=results,
                floating_point_used_for_acceptance=False,
                proof_scope='Exact finite premises and the seven pair-class proofs in the report.',
                elapsed_seconds=round(time.monotonic() - start, 3))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = verify()
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end='')
