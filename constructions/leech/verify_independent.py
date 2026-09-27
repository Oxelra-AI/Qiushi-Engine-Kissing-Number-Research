#!/usr/bin/env python3
"""Independent NumPy/SymPy check using shell-membership predicates, not generation.

No imports from verify.py. Integer matrix products and symbolic signs only.
The report proves the universal geometric implications.
"""
import argparse
import itertools
import json
import time
from collections import Counter
from pathlib import Path
import numpy as np
import sympy as s

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer_matrix(path):
    # NumPy loadtxt can coerce decimal-looking tokens to integers; reject them.
    rows = [list(map(int, line.split())) for line in Path(path).read_text().splitlines()
            if line.strip() and not line.lstrip().startswith('#')]
    return np.array(rows, dtype=np.int64)


def verify():
    start = time.monotonic()
    data = ROOT / 'data'
    g = integer_matrix(data / 'golay_generator.txt')
    require(g.shape == (12, 24) and np.isin(g, (0, 1)).all(), 'Bad generator')
    coefficients = np.array([[(i >> j) & 1 for j in range(12)] for i in range(4096)], dtype=np.int64)
    code = (coefficients @ g) % 2
    words = {tuple(r) for r in code}
    require(len(words) == 4096, 'Rank mismatch')
    require(Counter(map(int, code.sum(axis=1))) == {0:1, 8:759, 12:2576, 16:759, 24:1}, 'Weights')
    require(np.all((g @ g.T) % 2 == 0), 'Not self-orthogonal')
    octads = {tuple(r) for r in code if r.sum() == 8}

    def member(r):
        a = np.abs(r)
        if np.count_nonzero(a == 4) == 2 and np.count_nonzero(a) == 2:
            return True
        if np.count_nonzero(a == 2) == 8 and np.count_nonzero(a) == 8:
            return tuple((a > 0).astype(int)) in octads and np.count_nonzero(r < 0) % 2 == 0
        if np.count_nonzero(a == 3) == 1 and np.count_nonzero(a == 1) == 23:
            signs = (r < 0).astype(int)
            signs[np.argmax(a)] ^= 1
            return tuple(signs) in words
        return False

    blocks = []
    maxima = []
    for name in ['s496.txt', *[f'block{i}.txt' for i in range(4)]]:
        a = integer_matrix(data / name)
        require(a.shape == (496, 24), 'Block shape mismatch')
        require(np.all(np.abs(a) <= 4), 'Unsafe coordinate range')
        require(len({tuple(r) for r in a}) == 496, 'Duplicate row')
        require(all(member(r) for r in a), 'Shell membership failed')
        gram = a @ a.T
        require(np.all(np.diag(gram) == 32), 'Incorrect norm')
        maximum = int(gram[np.triu_indices(496, 1)].max())
        require(maximum <= 8, 'Internal dot bound failed')
        blocks.append(a); maxima.append(maximum)
    require(len({tuple(r) for a in blocks[1:] for r in a}) == 1984, 'Blocks overlap')
    tails = json.loads((data / 'tails.json').read_text())
    basis = [s.Integer(1), s.sqrt(2), s.sqrt(3), s.sqrt(6)]
    require(tails['basis'] == ['1', 'sqrt(2)', 'sqrt(3)', 'sqrt(6)'], 'Unknown field')
    def decode(key):
        require(len(tails[key]) == 12 and all(len(row) == 3 for row in tails[key])
                and all(len(v) == 4 for row in tails[key] for v in row), 'Tail coefficient shape')
        return [s.Matrix([sum(s.Rational(c) * b for c,b in zip(v,basis)) for v in row])
                for row in tails[key]]
    mixed, pure = decode('mixed'), decode('pure')
    require(len(mixed) == len(pure) == 12 and all(len(v) == 3 for v in mixed + pure), 'Tail shape')
    for v in mixed:
        require(s.simplify(v.dot(v)) == s.Rational(1,3), 'Mixed norm')
    for v in pure:
        require(s.simplify(v.dot(v)) == 1, 'Pure norm')
    require(len({tuple(v) for v in pure}) == 12, 'Pure duplicates')
    for a,b in itertools.combinations(pure, 2):
        require(s.simplify(s.Rational(1,2) - a.dot(b)).is_nonnegative is True, 'Pure bound')
    for a in pure:
        for b in mixed:
            require(s.simplify(s.Rational(1,2) - a.dot(b)).is_positive is True, 'Mixed/pure bound')
    gram = s.Matrix([[s.simplify(48*a.dot(b)) for b in mixed] for a in mixed])
    stored = s.Matrix(integer_matrix(data / 'tail_gram_scaled.txt').tolist())
    require(gram == stored, 'Gram mismatch')
    require(set(gram[i,j] for i in range(12) for j in range(i)) == {-16,-8,0,8}, 'Gram spectrum')
    partition = tails['partition']
    require(len(partition) == 4 and all(len(p) == 3 for p in partition)
            and sorted(sum(partition, [])) == list(range(12)), 'Partition mismatch')
    require(all(gram[i,j] <= -8 for p in partition for i,j in itertools.combinations(p,2)), 'Triple edges')
    require(not any(all(gram[i,j] <= -8 for i,j in itertools.combinations(c,2))
                    for c in itertools.combinations(range(12),4)), 'Unexpected four-clique')
    return dict(checker='Independent NumPy integer / SymPy algebraic checker', valid=True,
                results=[dict(dimension=25,lower_bound=197058),dict(dimension=27,lower_bound=200540)],
                shell_cardinality_from_disjoint_families=1104+759*128+4096*24,
                block_maxima=maxima, floating_point_used_for_acceptance=False,
                numpy_version=np.__version__, sympy_version=s.__version__,
                elapsed_seconds=round(time.monotonic() - start, 3))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    text = json.dumps(verify(), indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text)
    print(text,end='')
