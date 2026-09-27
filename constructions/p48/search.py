#!/usr/bin/env python3
"""Check the eight added lines and optionally search image families with exact unions."""
import argparse
import json
from pathlib import Path

import numpy as np

from verify import canon, load_integer_array, LAMBDAS, TAIL_SIZES

HERE = Path(__file__).resolve().parent


def multiply(a, b):
    bound = int(np.abs(a).max()) * int(np.abs(b).max()) * a.shape[1]
    if bound >= 2**63:
        raise ValueError('Matrix product exceeds int64 safety range')
    return a @ b


def lines(array):
    # Fixed-width little-endian row identities, not lossy numerical hashes.
    normalized = canon(array).astype('<i8')
    return {row.tobytes() for row in normalized}


def augmentation(c, g):
    if c.shape != (7077, 48):
        raise ValueError('Expected the archived 7077-line class')
    added = c[7069:]
    if not np.all(np.sum(multiply(added, g) * added, axis=1) == 6):
        raise ValueError('Added vector has wrong norm')
    product = multiply(multiply(added, g), c.T)
    for i in range(8):
        product[i, 7069 + i] = 0
    if np.abs(product).max() > 2 or len(lines(c)) != len(c):
        raise ValueError('Invalid or repeated augmentation line')
    return {'original_rows': 7069, 'added_rows': 8,
            'max_absolute_product_against_other_lines': int(np.abs(product).max())}


def select(images, count, starts):
    overlap = np.array([[len(a & b) for b in images] for a in images], dtype=np.int64)
    best, best_union = None, set()
    for start in range(min(starts, len(images))):
        chosen = [start]
        cost = overlap[start].copy()
        while len(chosen) < count:
            eligible = [i for i in range(len(images)) if i not in chosen]
            next_image = min(eligible, key=lambda i: (int(cost[i]), i))
            chosen.append(next_image)
            cost += overlap[next_image]
        union = set().union(*(images[i] for i in chosen))
        if len(union) > len(best_union):
            best, best_union = chosen, union
    return best, len(best_union)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--images', type=int, default=0, help='Optional new image pool; zero checks saved families')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--word-length', type=int, default=30)
    parser.add_argument('--starts', type=int, default=50)
    args = parser.parse_args()
    if args.output.exists() or args.images < 0 or args.word_length < 0 or args.starts < 1:
        parser.error('Use a new output directory and valid search parameters')
    c = load_integer_array(HERE / 'data/class_p48_7077.npy')
    g = load_integer_array(HERE / 'data/p48p_gram.npy')
    generators = load_integer_array(HERE / 'data/p48p_gens.npy')
    result = {'augmentation': augmentation(c, g), 'families': {}}
    for dimension, count in LAMBDAS.items():
        matrices = ([np.eye(48, dtype=np.int64)] if dimension == 49 else
                    load_integer_array(HERE / f'data/dim{dimension}_group_elems.npy'))
        union = set()
        original_union = set()
        sizes = []
        for matrix in matrices:
            if not np.array_equal(multiply(multiply(matrix, g), matrix.T), g):
                raise ValueError('A saved matrix is not an isometry')
            image = lines(multiply(c, matrix))
            sizes.append(len(image - union))
            union.update(image)
            original_union.update(lines(multiply(c[:7069], matrix)))
        result['families'][dimension] = {'images': count, 'union': len(union),
                                         'same_family_original_class_union': len(original_union),
                                         'extra_lines_from_augmentation': len(union) - len(original_union),
                                         'assigned_sizes': sizes, 'overlap_loss': count * len(c) - len(union),
                                         'points': 52416000 + 2 * len(union) + TAIL_SIZES[dimension]}
    chosen_matrices = {}
    if args.images:
        rng = np.random.default_rng(args.seed)
        matrices = [np.eye(48, dtype=np.int64)]
        for _ in range(1, args.images):
            matrix = np.eye(48, dtype=np.int64)
            for _ in range(args.word_length):
                matrix = multiply(matrix, generators[rng.integers(len(generators))])
            if not np.array_equal(multiply(multiply(matrix, g), matrix.T), g):
                raise ValueError('Generated matrix is not an isometry')
            matrices.append(matrix)
        images = [lines(multiply(c, matrix)) for matrix in matrices]
        result['search'] = {'images': args.images, 'seed': args.seed,
                            'word_length': args.word_length, 'starts': args.starts, 'families': {}}
        for dimension, count in LAMBDAS.items():
            if count > len(images):
                continue
            selected, size = select(images, count, args.starts)
            chosen_matrices[dimension] = np.array([matrices[i] for i in selected])
            result['search']['families'][dimension] = {'image_indices': selected, 'union': size,
                                                     'points': 52416000 + 2 * size + TAIL_SIZES[dimension]}
    args.output.mkdir(parents=True, exist_ok=False)
    for dimension, matrices in chosen_matrices.items():
        np.save(args.output / f'dim{dimension}_group_elems.npy', matrices)
    (args.output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
