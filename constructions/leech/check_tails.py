#!/usr/bin/env python3
"""Check the common orthogonal change from archived tails to the D3 model.

The archived coordinates and labels are never rewritten. This supplementary
identity check uses exact SymPy expressions, not approximate point matching.
"""
import argparse
import itertools
import json
from pathlib import Path
import sympy as s

ROOT = Path(__file__).resolve().parent


def verify():
    data = json.loads((ROOT / 'data/tails.json').read_text())
    basis = (s.Integer(1), s.sqrt(2), s.sqrt(3), s.sqrt(6))
    def decode(key):
        return s.Matrix([[sum(s.Rational(c) * b for c, b in zip(v, basis))
                          for v in row] for row in data[key]])
    O = s.Matrix([[s.sqrt(2)/2, 0, s.sqrt(2)/2],
                  [-s.sqrt(6)/6, s.sqrt(6)/3, s.sqrt(6)/6],
                  [-s.sqrt(3)/3, -s.sqrt(3)/3, s.sqrt(3)/3]])
    R = s.Matrix([[1/s.sqrt(2), -1/s.sqrt(2), 0],
                  [1/s.sqrt(2), 1/s.sqrt(2), 0], [0, 0, 1]])
    if s.simplify(O.T * O) != s.eye(3) or s.simplify(R.T * R) != s.eye(3):
        raise ValueError('Nonorthogonal change of coordinates')
    mixed = s.simplify(s.sqrt(6) * decode('mixed') * O)
    pure = s.simplify(s.sqrt(2) * decode('pure') * O * R)
    roots = sorted(v for v in itertools.product((-1, 0, 1), repeat=3)
                   if sum(c*c for c in v) == 2)
    rows = lambda M: [tuple(M.row(i)) for i in range(M.rows)]
    if sorted(rows(mixed)) != roots or sorted(rows(pure)) != roots:
        raise ValueError('The same orthogonal map does not identify both tail sets')
    gram = 8 * mixed * mixed.T
    stored = s.Matrix([[int(x) for x in line.split()]
                       for line in (ROOT / 'data/tail_gram_scaled.txt').read_text().splitlines()
                       if line.strip() and not line.startswith('#')])
    if gram != stored:
        raise ValueError('Canonical model changed the archived mixed-label order')
    for triple in data['partition']:
        if sum((mixed.row(i) for i in triple), s.zeros(1, 3)) != s.zeros(1, 3):
            raise ValueError('An archived triple is not a zero-sum D3 triangle')
    V = s.Matrix(roots)
    products = V * R.T * V.T / s.sqrt(12)
    maximum = (s.sqrt(6) + 2*s.sqrt(3))/12
    if not any(s.simplify(p - maximum) == 0 for p in products):
        raise ValueError('The stated cross maximum is not attained')
    if not all(s.simplify(maximum-p).is_nonnegative is True for p in products):
        raise ValueError('The stated cross maximum is exceeded')
    if s.simplify(s.Rational(1,2)-maximum).is_positive is not True:
        raise ValueError('The cross bound is not strictly below one half')
    return dict(valid=True, row_convention='archived row multiplied on the right by O',
                mixed_D3_roots_by_archived_label=[list(map(int, row)) for row in rows(mixed)],
                pure_D3_roots_by_archived_label=[list(map(int, row)) for row in rows(pure)],
                mixed_permutation_to_lexicographic_D3=[roots.index(row) for row in rows(mixed)],
                pure_permutation_to_lexicographic_D3=[roots.index(row) for row in rows(pure)],
                partition=data['partition'], cross_maximum=str(maximum),
                archived_gram_preserved=True, floating_point_acceptance=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(verify(), indent=2) + '\n'
    if args.output:
        args.output.write_text(result)
    print(result, end='')
