#!/usr/bin/env python3
"""Exact verifier for the three-layer ERS specialization and affine sign codes.

The sign code occupies n0 <= n coordinates, padded with zeros when n0 < n.
In this paper, n0 is 32 for ambient dimensions 33, 34 and 37, and equals the
ambient dimension for 38 and 39. Source attribution is in the import manifest.

Inputs:
  * binary linear kernel generator and affine coset representatives on n0 bits;
  * a length-n constant-weight code A(n,8,8) as hex masks;
  * an optional current lower-bound reference for K(n).

It verifies by exact integer arithmetic:
  * top kernel rank/span/minimum distance and pairwise coset distances;
  * support code: distinct length-n weight-8 words, in range, |B cap B'|<=4,
    and no repeated 5-subset;
  * the ERS layer inequalities for unit vectors on supports n0, 8, and 2;
  * the count |top| + 128 |support| + 4 binom(n,2).

No floating point tolerance is used.  Bit positions are 0-based and top vectors
are embedded on coordinates 0,...,n0-1 of R^n.
"""
import argparse, hashlib, itertools, json, math, time
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def read_hex_file(path):
    vals = []
    for line in Path(path).read_text().splitlines():
        s = line.strip()
        if not s or s.startswith('#') or s.startswith('$'):
            continue
        vals.append(int(s, 16))
    return vals


def rref(rows, n):
    piv = {}
    mask = (1 << n) - 1
    for row in rows:
        x = row & mask
        while x:
            b = x.bit_length() - 1
            if b in piv:
                x ^= piv[b]
            else:
                piv[b] = x
                break
    # remove pivot bit from all other rows, leaving a deterministic reduced basis
    for b in sorted(list(piv), reverse=True):
        row = piv[b]
        for b2 in list(piv):
            if b2 != b and ((piv[b2] >> b) & 1):
                piv[b2] ^= row
    return [piv[b] for b in sorted(piv, reverse=True)]


def reduce_by_basis(x, basis):
    y = x
    for b in basis:
        p = b.bit_length() - 1
        if (y >> p) & 1:
            y ^= b
    return y


def span_words(basis):
    words = [0]
    for b in basis:
        words += [w ^ b for w in words]
    return words


def rank_comb(c):
    # injective combinadic rank for a sorted tuple of zero-based coordinates
    return sum(math.comb(a, i) for i, a in enumerate(c, start=1))


def verify_top(n0, kernel_path, reps_path):
    rows = read_hex_file(kernel_path)
    reps = read_hex_file(reps_path)
    kernel_in_range = all(0 <= g < (1 << n0) for g in rows)
    reps_in_range = all(0 <= r < (1 << n0) for r in reps)
    basis = rref(rows, n0)
    words = span_words(basis)
    hist = {}
    kmind = 10**9
    for w in words[1:]:
        wt = w.bit_count()
        hist[wt] = hist.get(wt, 0) + 1
        kmind = min(kmind, wt)
    if kmind == 10**9:
        kmind = 0
    reductions = [reduce_by_basis(r, basis) for r in reps]
    pair = []
    pmind = 10**9
    for i in range(len(reps)):
        for j in range(i + 1, len(reps)):
            diff = reps[i] ^ reps[j]
            best = min((diff ^ w).bit_count() for w in words)
            pair.append({'i': i, 'j': j, 'distance': best})
            pmind = min(pmind, best)
    if pmind == 10**9:
        pmind = kmind
    dreq = (n0 + 3) // 4
    return {
        'top_length_n0': n0,
        'kernel_file': str(kernel_path),
        'kernel_sha256': sha256(kernel_path),
        'reps_file': str(reps_path),
        'reps_sha256': sha256(reps_path),
        'kernel_in_range': kernel_in_range,
        'reps_in_range': reps_in_range,
        'rank': len(basis),
        'kernel_words': len(words),
        'kernel_span_distinct': len(set(words)) == len(words),
        'kernel_min_distance': kmind,
        'kernel_weight_histogram_nonzero': {str(k): v for k, v in sorted(hist.items())},
        'coset_count': len(reps),
        'distinct_cosets': len(set(reductions)) == len(reductions),
        'pair_coset_distances': pair,
        'minimum_between_cosets': pmind,
        'top_min_distance': min(kmind, pmind),
        'required_top_distance': dreq,
        'top_size': len(reps) * len(words),
        'valid_top_sign_code': (kernel_in_range and reps_in_range and len(set(words)) == len(words)
                                and kmind >= dreq and pmind >= dreq
                                and len(set(reductions)) == len(reductions)),
    }


def verify_support(n, support_path):
    blocks = read_hex_file(support_path)
    hist = {}
    mind = 999
    bad = []
    seen = set()
    five = set()
    for idx, x in enumerate(blocks):
        if x in seen and len(bad) < 5:
            bad.append({'type': 'duplicate', 'index': idx})
        seen.add(x)
        if x.bit_count() != 8 and len(bad) < 5:
            bad.append({'type': 'weight', 'index': idx, 'weight': x.bit_count()})
        if not (0 <= x < (1 << n)) and len(bad) < 5:
            bad.append({'type': 'range', 'index': idx})
        bits = [i for i in range(n) if (x >> i) & 1]
        for c in itertools.combinations(bits, 5):
            five.add(rank_comb(c))
    for i, x in enumerate(blocks):
        for j in range(i + 1, len(blocks)):
            inter = (x & blocks[j]).bit_count()
            hist[inter] = hist.get(inter, 0) + 1
            mind = min(mind, 16 - 2 * inter)
            if inter > 4 and len(bad) < 5:
                bad.append({'type': 'intersection', 'i': i, 'j': j, 'intersection': inter})
    expected5 = len(blocks) * math.comb(8, 5)
    return {
        'support_file': str(support_path),
        'support_sha256': sha256(support_path),
        'size': len(blocks),
        'distinct': len(seen) == len(blocks),
        'weight_8': all(x.bit_count() == 8 for x in blocks),
        'in_range': all(0 <= x < (1 << n) for x in blocks),
        'pair_intersection_histogram': {str(k): v for k, v in sorted(hist.items())},
        'min_hamming_distance': mind if len(blocks) > 1 else 0,
        'distinct_5_subsets': len(five),
        'expected_5_subsets': expected5,
        'valid_support_code': not bad and len(five) == expected5,
        'bad_first': bad[:5],
    }


def geometry_checks(n, n0, top_min_distance, support_ok):
    # Unit-norm ERS vectors.  Inequalities are squared where radicals occur.
    checks = []
    checks.append({
        'layer_pair': 'top-top',
        'formula': '1 - 2*d_top/n0 <= 1/2',
        'left_times_2n0': 2 * (n0 - 2 * top_min_distance),
        'right_times_2n0': n0,
        'ok': 2 * (n0 - 2 * top_min_distance) <= n0,
    })
    checks.append({
        'layer_pair': 'top-middle',
        'formula': 'sqrt(8/n0) <= 1/2, squared as 32 <= n0',
        'left_squared_times_4n0': 32,
        'right_squared_times_4n0': n0,
        'ok': 32 <= n0,
    })
    checks.append({
        'layer_pair': 'top-bottom',
        'formula': 'sqrt(2/n0) <= 1/2, squared as 8 <= n0',
        'left_squared_times_4n0': 8,
        'right_squared_times_4n0': n0,
        'ok': 8 <= n0,
    })
    checks.append({
        'layer_pair': 'middle-middle same support',
        'formula': 'distinct even-parity length-8 signs differ in at least two positions, sign dot <=4, normalized dot <=1/2',
        'ok': True,
    })
    checks.append({
        'layer_pair': 'middle-middle different supports',
        'formula': 'support intersections <=4, aligned normalized dot <=4/8=1/2',
        'ok': support_ok,
    })
    checks.append({
        'layer_pair': 'middle-bottom',
        'formula': 'two common coordinates give 2/sqrt(8*2)=1/2',
        'ok': support_ok,
    })
    checks.append({
        'layer_pair': 'bottom-bottom',
        'formula': 'two 2-supports intersect in at most one coordinate, or same support distinct signs have dot <=0',
        'ok': True,
    })
    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True, help='ambient kissing dimension')
    ap.add_argument('--n0', type=int, required=True, help='top sign-code support length')
    ap.add_argument('--kernel', required=True)
    ap.add_argument('--reps', required=True)
    ap.add_argument('--support', required=True)
    ap.add_argument('--reference', type=int, default=None)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    t0 = time.time()
    if args.n0 > args.n:
        raise ValueError('top support length n0 must satisfy n0 <= n')
    top = verify_top(args.n0, args.kernel, args.reps)
    support = verify_support(args.n, args.support)
    geom = geometry_checks(args.n, args.n0, top['top_min_distance'], support['valid_support_code'])
    pair_layer = 4 * math.comb(args.n, 2)
    total = top['top_size'] + 128 * support['size'] + pair_layer
    valid_configuration = (args.n0 <= args.n and top['valid_top_sign_code']
                           and support['valid_support_code'] and all(c['ok'] for c in geom))
    beats_reference = (None if args.reference is None else total > args.reference)
    result = {
        'schema': 'ers_variable_top_package_verifier_v1',
        'ambient_dimension_n': args.n,
        'top_support_length_n0': args.n0,
        'top_embedding': 'first n0 coordinates with zeros in coordinates n0..n-1',
        'top': top,
        'support': support,
        'middle_signings_per_support': 128,
        'pair_layer_size': pair_layer,
        'geometry_checks': geom,
        'total': total,
        'reference_lower_bound': args.reference,
        'improvement': (total - args.reference if args.reference is not None else None),
        'valid_configuration': valid_configuration,
        'beats_reference': beats_reference,
        'valid': valid_configuration and (args.reference is None or beats_reference),
        'elapsed_seconds': round(time.time() - t0, 3),
    }
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    if not result['valid']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
