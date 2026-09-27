#!/usr/bin/env python3
"""Reconstruct the 3125-vertex second-layer graph; optionally optimize its labels."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'lib'))
from leech import build


def candidate_graph():
    shell = build().astype(np.int64)
    heads = np.load(HERE / 'data/heads27_Y.npy', allow_pickle=False).astype(np.int64)
    if shell.shape != (196560, 24) or heads.shape != (2258, 24):
        raise ValueError('Unexpected shell or first-layer shape')
    if np.max(np.abs(shell)) > 4 or np.max(np.abs(heads)) > 16:
        raise ValueError('Coordinates exceed the checked integer range')
    keep = np.zeros(len(shell), dtype=bool)
    for start in range(0, len(shell), 512):
        # A first-layer deletion has dot > 48, hence cannot pass this screen.
        keep[start:start + 512] = np.max(shell[start:start + 512] @ heads.T, axis=1) <= 32
    candidates = shell[keep]
    products = candidates @ candidates.T
    edges = np.column_stack(np.where(np.triu(products > 8, 1)))
    return candidates, edges


def check_selection(candidates, edges, owners, labels):
    lookup = {tuple(map(int, row)): i for i, row in enumerate(candidates)}
    if len(owners) != len(labels) or len({tuple(row) for row in owners}) != len(owners):
        raise ValueError('Repeated owner or inconsistent labels')
    selected = {}
    for row, label in zip(owners, labels):
        if tuple(row) not in lookup or int(label) not in range(3):
            raise ValueError('Invalid owner or label')
        selected[lookup[tuple(row)]] = int(label)
    for u, v in edges:
        if int(u) in selected and selected.get(int(v)) == selected[int(u)]:
            raise ValueError('Conflicting same-label owners')
    return selected


def solve(candidates, edges, selected, seconds, workers, seed):
    from ortools.sat.python import cp_model
    model = cp_model.CpModel()
    z = [[model.new_bool_var(f'z_{i}_{j}') for j in range(3)] for i in range(len(candidates))]
    for row in z:
        model.add(sum(row) <= 1)
    for u, v in edges:
        for j in range(3):
            model.add(z[int(u)][j] + z[int(v)][j] <= 1)
    for i, j in selected.items():
        for k in range(3):
            model.add_hint(z[i][k], int(j == k))
    model.maximize(sum(value for row in z for value in row))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    status = solver.solve(model)
    info = {'status': solver.status_name(status), 'best_bound': solver.best_objective_bound}
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return info, None, None
    choice = [(i, j) for i, row in enumerate(z) for j, value in enumerate(row) if solver.value(value)]
    owners = candidates[[i for i, _ in choice]]
    labels = np.array([j for _, j in choice], dtype=np.int64)
    check_selection(candidates, edges, owners, labels)
    info['selected'] = len(owners)
    return info, owners, labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=0, help='Optional CP-SAT time; zero only reconstructs')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--seed', type=int, default=0)
    args = parser.parse_args()
    if args.output.exists() or args.seconds < 0 or args.workers < 1:
        parser.error('Use a new output directory and nonnegative search time')
    candidates, edges = candidate_graph()
    owners = np.load(HERE / 'data/heads27_layer2_u.npy', allow_pickle=False)
    labels = np.load(HERE / 'data/heads27_layer2_line.npy', allow_pickle=False)
    selected = check_selection(candidates, edges, owners, labels)
    result = {'candidates': len(candidates), 'edges': len(edges), 'saved_owners': len(selected),
              'label_sizes': np.bincount(labels.astype(int), minlength=3).tolist(),
              'candidate_sha256': hashlib.sha256(candidates.tobytes()).hexdigest(),
              'edge_sha256': hashlib.sha256(edges.astype('<i8').tobytes()).hexdigest()}
    if args.seconds:
        info, new_owners, new_labels = solve(candidates, edges, selected, args.seconds, args.workers, args.seed)
        result['search'] = info
    args.output.mkdir(parents=True, exist_ok=False)
    np.save(args.output / 'candidates.npy', candidates)
    np.save(args.output / 'edges.npy', edges)
    if args.seconds and new_owners is not None:
        np.save(args.output / 'owners.npy', new_owners)
        np.save(args.output / 'labels.npy', new_labels)
    (args.output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
