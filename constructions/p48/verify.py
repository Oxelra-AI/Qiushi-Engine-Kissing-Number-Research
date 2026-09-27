#!/usr/bin/env python3
"""
Independent exact verification of the 7077-line P48p cap witnesses for dimensions 49--55.

Checks the P48p Gram matrix and generators, the 7077-line class, automorphism
images, tail root systems A1,A2,A3,D4,D5,E6,E7, and cap lifting inequalities
in exact arithmetic. The ambient minimum squared norm six and 52,416,000-point
minimal shell are supplied by the cited lattice catalogue and the paper.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path
from fractions import Fraction
from itertools import product

import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
FAM7077 = DATA
EXT = DATA

N48 = 52_416_000
T = Fraction(3, 4)
ONE_MINUS_T = Fraction(1, 4)
SQRT_T_SQUARED = T

LAMBDAS = {49: 1, 50: 3, 51: 6, 52: 12, 53: 20, 54: 36, 55: 63}
TAIL_SIZES = {49: 2, 50: 6, 51: 12, 52: 24, 53: 40, 54: 72, 55: 126}
PUBLIC = {
    49: 52_430_140,
    50: 52_458_418,
    51: 52_500_816,
    52: 52_585_516,
    53: 52_698_222,
    54: 52_922_906,
    55: 53_299_730,
}


def load_integer_array(path: str | Path) -> np.ndarray:
    array = np.load(path, allow_pickle=False)
    if array.dtype.kind not in 'iu':
        raise ValueError(f'{Path(path).name}: expected an integer array')
    limit = 2**63 - 1
    if array.size and (int(array.min()) < -limit or int(array.max()) > limit):
        raise ValueError(f'{Path(path).name}: entries exceed exact int64 absolute-value range')
    return array.astype(np.int64)


def sha256_array(a: np.ndarray) -> str:
    b = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(str(b.shape).encode())
    h.update(str(b.dtype).encode())
    h.update(b.tobytes())
    return h.hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def strip_html(s: str) -> str:
    return re.sub(r'<[^>]*>', ' ', s)


def ints_between(raw: str, a: str, b: str) -> list[int]:
    blk = strip_html(raw[raw.index(a):raw.index(b)])
    return [int(t) for t in blk.split() if re.fullmatch(r'-?\d+', t)]


def parse_catalogue_p48p() -> tuple[np.ndarray, np.ndarray, int]:
    """Parse P48p.html directly and return (Gram, generators, MINIMAL_NORM)."""
    html = os.path.join(DATA, 'P48p.html')
    raw = open(html, 'r', encoding='latin-1').read()
    nums = ints_between(raw, '<a NAME="GRAM">', '<a NAME="MINIMAL_NORM">')
    if nums[0] == 48 and nums[1] == 48 and len(nums) == 2 + 48 * 48:
        G_cat = np.array(nums[2:], dtype=np.int64).reshape(48, 48)
    else:
        raise ValueError(f'unexpected P48p Gram layout: first entries {nums[:4]}, len={len(nums)}')
    nums = ints_between(raw, '<a NAME="GROUP_GENERATORS">', '<a NAME="PROPERTIES">')
    ngen = nums[0]
    rest = nums[1:]
    if len(rest) != ngen * (2 + 48 * 48):
        raise ValueError(f'unexpected generator block length {len(rest)} for {ngen} generators')
    gens = np.empty((ngen, 48, 48), dtype=np.int64)
    for g in range(ngen):
        base = g * (2 + 48 * 48)
        if rest[base] != 48 or rest[base + 1] != 48:
            raise ValueError('unexpected generator shape marker')
        gens[g] = np.array(rest[base + 2:base + 2 + 48 * 48], dtype=np.int64).reshape(48, 48)
    m = re.search(r'<a NAME="MINIMAL_NORM"><STRONG>MINIMAL_NORM</STRONG></a><br>\s*([0-9]+)<br>', raw)
    if not m:
        raise ValueError('MINIMAL_NORM field not found')
    return G_cat, gens, int(m.group(1))


def int64_safety_bound(max_left: int, max_right: int, n_terms: int) -> int:
    return int(max_left) * int(max_right) * int(n_terms)


def bareiss_det(M: np.ndarray) -> int:
    """Exact determinant by fraction-free Bareiss elimination."""
    A = [[int(x) for x in row] for row in np.asarray(M).tolist()]
    n = len(A)
    sign = 1
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            swap = None
            for i in range(k + 1, n):
                if A[i][k] != 0:
                    swap = i
                    break
            if swap is None:
                return 0
            A[k], A[swap] = A[swap], A[k]
            sign *= -1
        pivot = A[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                num = A[i][j] * pivot - A[i][k] * A[k][j]
                if num % prev != 0:
                    raise ArithmeticError('Bareiss division not exact')
                A[i][j] = num // prev
        prev = pivot
        # Entries below/right are all that matter after this point.
        for i in range(k + 1, n):
            A[i][k] = 0
    return sign * A[n - 1][n - 1]


def rank_q(M: np.ndarray) -> int:
    """Exact rank over Q for small integer matrices."""
    A = [[Fraction(int(x), 1) for x in row] for row in np.asarray(M).tolist()]
    if not A:
        return 0
    m = len(A)
    n = len(A[0])
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, m):
            if A[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                fac = A[i][c]
                A[i] = [A[i][j] - fac * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def canon(V: np.ndarray) -> np.ndarray:
    V = np.asarray(V, dtype=np.int64)
    if V.ndim == 1:
        V = V.reshape(1, -1)
    nz = V != 0
    first = np.argmax(nz, axis=1)
    signs = np.sign(V[np.arange(len(V)), first]).astype(np.int64)
    return V * signs[:, None]


def row_set(V: np.ndarray) -> set[tuple[int, ...]]:
    return set(map(tuple, np.asarray(V, dtype=np.int64).tolist()))


def max_abs_offdiag_blocked(C: np.ndarray, G: np.ndarray, block: int = 512) -> int:
    n = len(C)
    maxv = 0
    GCt = G @ C.T
    for i in range(0, n, block):
        B = C[i:i + block] @ GCt
        for r in range(B.shape[0]):
            B[r, i + r] = 0
        local = int(np.abs(B).max()) if B.size else 0
        if local > maxv:
            maxv = local
    return maxv


def e8_roots_scaled_by_2() -> np.ndarray:
    roots: list[tuple[int, ...]] = []
    # D8 roots: actual roots have entries ±1,±1; scaled by 2.
    for i in range(8):
        for j in range(i + 1, 8):
            for si in (-2, 2):
                for sj in (-2, 2):
                    v = [0] * 8
                    v[i] = si
                    v[j] = sj
                    roots.append(tuple(v))
    # Half roots: actual roots have all entries ±1/2 with even number of minuses; scaled by 2.
    for signs in product((-1, 1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(signs))
    R = np.array(roots, dtype=np.int64)
    assert R.shape == (240, 8)
    assert np.all(np.einsum('ij,ij->i', R, R) == 8)
    return R


def tail_roots(k: int) -> tuple[np.ndarray, int, str]:
    """Return integer coordinates, their common squared norm, and the root-system name."""
    if k == 1:
        return np.array([[1], [-1]], dtype=np.int64), 1, 'A1'
    if k == 2:
        roots = []
        for i in range(3):
            for j in range(3):
                if i != j:
                    v = [0, 0, 0]
                    v[i] = 1
                    v[j] = -1
                    roots.append(tuple(v))
        return np.array(roots, dtype=np.int64), 2, 'A2 in {sum=0} subset R^3'
    if k in (3, 4, 5):
        roots = []
        for i in range(k):
            for j in range(i + 1, k):
                for si in (-1, 1):
                    for sj in (-1, 1):
                        v = [0] * k
                        v[i] = si
                        v[j] = sj
                        roots.append(tuple(v))
        name = 'A3=D3' if k == 3 else f'D{k}'
        return np.array(roots, dtype=np.int64), 2, name
    if k == 6:
        R = e8_roots_scaled_by_2()
        a1 = np.array([2, -2, 0, 0, 0, 0, 0, 0], dtype=np.int64)
        a2 = np.array([0, 2, -2, 0, 0, 0, 0, 0], dtype=np.int64)
        keep = (R @ a1 == 0) & (R @ a2 == 0)
        return R[keep], 8, 'E6 as E8 roots orthogonal to A2, scaled by 2'
    if k == 7:
        R = e8_roots_scaled_by_2()
        a1 = np.array([2, -2, 0, 0, 0, 0, 0, 0], dtype=np.int64)
        keep = (R @ a1 == 0)
        return R[keep], 8, 'E7 as E8 roots orthogonal to A1, scaled by 2'
    raise ValueError(k)


def verify_tail_code(k: int) -> dict:
    roots, norm2, name = tail_roots(k)
    n = len(roots)
    dim_rank = rank_q(roots)
    norms = np.einsum('ij,ij->i', roots, roots)
    gram = roots @ roots.T
    np.fill_diagonal(gram, -10**9)
    max_offdiag = int(gram.max())
    line_reps = canon(roots)
    lines = row_set(line_reps)
    max_abs_line_ip = None
    reps = np.array(sorted(lines), dtype=np.int64)
    if len(reps) > 1:
        Lg = reps @ reps.T
        np.fill_diagonal(Lg, 0)
        max_abs_line_ip = int(np.abs(Lg).max())
    else:
        max_abs_line_ip = 0
    expected_tau = {1: 2, 2: 6, 3: 12, 4: 24, 5: 40, 6: 72, 7: 126}[k]
    expected_lines = expected_tau // 2
    return {
        'k': k,
        'name': name,
        'ambient_coordinate_columns': int(roots.shape[1]),
        'rank_over_Q': dim_rank,
        'num_tail_points': n,
        'num_antipodal_lines': len(lines),
        'integer_squared_norm': norm2,
        'max_offdiag_integer_ip': max_offdiag,
        'max_abs_line_integer_ip': max_abs_line_ip,
        'point_code_ok': bool(n == expected_tau and dim_rank == k and np.all(norms == norm2) and 2 * max_offdiag <= norm2),
        'line_code_ok': bool(len(lines) == expected_lines and 2 * max_abs_line_ip <= norm2),
        'sha256_roots': sha256_array(roots),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    failures: list[str] = []
    def require(cond: bool, msg: str) -> None:
        status = 'PASS' if cond else 'FAIL'
        print(f'[{status}] {msg}')
        if not cond:
            failures.append(msg)

    print('=' * 78)
    print('P48p 7077-line cap construction verification for dimensions 49--55')
    print('=' * 78)

    G = load_integer_array(DATA / 'p48p_gram.npy')
    GE = load_integer_array(DATA / 'p48p_gens.npy')
    C = load_integer_array(EXT / 'class_p48_7077.npy')

    print('\n1. Catalogue P48p Gram matrix and automorphisms')
    cat_html = os.path.join(DATA, 'P48p.html')
    G_cat, GE_cat, cat_min_norm = parse_catalogue_p48p()
    detG = bareiss_det(G)
    require(np.array_equal(G, G_cat), 'loaded p48p_gram.npy equals the Gram parsed directly from P48p.html')
    require(np.array_equal(GE, GE_cat), 'loaded p48p_gens.npy equals the generators parsed directly from P48p.html')
    require(G.shape == (48, 48), f'Gram shape is {G.shape}')
    require(np.array_equal(G, G.T), 'Gram is symmetric')
    require(np.all(np.diag(G) % 2 == 0), 'Gram has even diagonal')
    # Sylvester criterion, checked exactly on all leading principal minors.
    leading_minors_positive = True
    first_bad_minor = None
    for r in range(1, 49):
        d_r = bareiss_det(G[:r, :r])
        if d_r <= 0:
            leading_minors_positive = False
            first_bad_minor = (r, d_r)
            break
    require(leading_minors_positive, f'Gram is positive definite by exact leading-principal-minor check; first bad={first_bad_minor}')
    require(detG == 1, f'Bareiss determinant is exactly {detG}')
    require(cat_min_norm == 6, f'Catalogue P48p.html reports MINIMAL_NORM {cat_min_norm}')

    int64_limit = 2**63 - 1
    maxG = int(np.abs(G).max())
    maxGE = int(np.abs(GE).max())
    gen_left_bound = int64_safety_bound(maxGE, maxG, 48)
    gen_iso_bound = int64_safety_bound(gen_left_bound, maxGE, 48)
    require(gen_iso_bound < int64_limit, f'int64 safe for published generator isometry products; worst bound {gen_iso_bound} < 2^63')
    for i, A in enumerate(GE):
        require(np.array_equal(A @ G @ A.T, G), f'published generator {i} preserves G exactly')

    print('\n2. The 7077-line mother class')
    require(C.shape == (7077, 48), f'extended class shape is {C.shape}')
    maxC = int(np.abs(C).max())
    class_left_bound = int64_safety_bound(maxC, maxG, 48)
    class_ip_bound = int64_safety_bound(maxC, class_left_bound, 48)
    require(class_ip_bound < int64_limit, f'int64 safe for class norm/IP products; worst bound {class_ip_bound} < 2^63')
    Cc = canon(C)
    require(len(row_set(Cc)) == len(C), 'all class lines are distinct up to sign')
    norms = np.einsum('ij,jk,ik->i', C, G, C)
    require(np.all(norms == 6), 'every mother-class vector has P48p norm 6')
    max_class_ip = max_abs_offdiag_blocked(C, G)
    require(max_class_ip <= 2, f'max |inner product| inside mother class is {max_class_ip} <= 2')

    print('\n3. Tail root systems and antipodal line counts')
    tail_info_by_dim = {}
    for dim in range(49, 56):
        k = dim - 48
        info = verify_tail_code(k)
        tail_info_by_dim[dim] = info
        require(info['point_code_ok'], f'dim {dim}: {info["name"]} gives {info["num_tail_points"]} tail points in rank {info["rank_over_Q"]} with pairwise IP <= 1/2')
        require(info['line_code_ok'], f'dim {dim}: tail has {info["num_antipodal_lines"]} antipodal lines = lambda')
        require(info['num_antipodal_lines'] == LAMBDAS[dim], f'dim {dim}: lambda {LAMBDAS[dim]} matches tail-line count')

    print('\n4. Automorphism-image families, exact unions, and counts')
    results: dict[int, dict] = {}
    used_line_hashes_by_dim: dict[int, str] = {}
    C_tuple_set = row_set(Cc)
    require(len(C_tuple_set) == 7077, 'canonical mother-class tuple set has size 7077')

    # Dimension 49 uses the mother class itself.
    S49 = len(C)
    tau49 = N48 + 2 * S49 + TAIL_SIZES[49]
    results[49] = {
        'dimension': 49,
        'k': 1,
        'lambda': 1,
        'S': S49,
        'tail_points': TAIL_SIZES[49],
        'kissing_lower_bound': tau49,
        'public_comparison': PUBLIC[49],
        'strict_gain': tau49 - PUBLIC[49],
        'assigned_class_sizes': [S49],
    }
    require(tau49 > PUBLIC[49], f'dim 49 count {tau49} exceeds public {PUBLIC[49]} by {tau49 - PUBLIC[49]}')

    for dim in range(50, 56):
        lam = LAMBDAS[dim]
        g_path = os.path.join(FAM7077, f'dim{dim}_group_elems.npy')
        require(os.path.exists(g_path), f'dim {dim}: group element file exists')
        gs = load_integer_array(g_path)
        require(gs.shape == (lam, 48, 48), f'dim {dim}: loaded {gs.shape[0]} group elements for lambda={lam}')
        maxA = int(np.abs(gs).max())
        fam_left_bound = int64_safety_bound(maxA, maxG, 48)
        fam_iso_bound = int64_safety_bound(fam_left_bound, maxA, 48)
        image_bound = int64_safety_bound(maxC, maxA, 48)
        require(maxA <= 32, f'dim {dim}: max |family matrix entry| = {maxA}')
        require(fam_iso_bound < int64_limit, f'dim {dim}: int64 safe for family isometry products; worst bound {fam_iso_bound} < 2^63')
        require(image_bound < int64_limit, f'dim {dim}: int64 safe for C @ A image products; worst bound {image_bound} < 2^63')
        for i, A in enumerate(gs):
            require(np.array_equal(A @ G @ A.T, G), f'dim {dim}: family element {i} is a P48p isometry')
        all_lines: set[tuple[int, ...]] = set()
        assigned_sizes: list[int] = []
        overlap_with_previous: list[int] = []
        for A in gs:
            image = canon(C @ A)
            lines_i = row_set(image)
            require(len(lines_i) == 7077, f'dim {dim}: image has 7077 distinct lines')
            new_lines = lines_i - all_lines
            overlap_with_previous.append(len(lines_i) - len(new_lines))
            assigned_sizes.append(len(new_lines))
            all_lines |= lines_i
        S = len(all_lines)
        tau = N48 + 2 * S + TAIL_SIZES[dim]
        gain = tau - PUBLIC[dim]
        require(S == sum(assigned_sizes), f'dim {dim}: assigned disjoint class sizes sum to union S={S}')
        if dim == 50:
            require(S == lam * 7077, 'dim 50: three 7077-line images are exactly pairwise disjoint')
        require(gain > 0, f'dim {dim} count {tau} exceeds public {PUBLIC[dim]} by {gain}')
        h = hashlib.sha256()
        for row in sorted(all_lines):
            h.update(np.array(row, dtype=np.int64).tobytes())
        used_line_hashes_by_dim[dim] = h.hexdigest()
        results[dim] = {
            'dimension': dim,
            'k': dim - 48,
            'lambda': lam,
            'S': S,
            'tail_points': TAIL_SIZES[dim],
            'kissing_lower_bound': tau,
            'public_comparison': PUBLIC[dim],
            'strict_gain': gain,
            'assigned_class_sizes': assigned_sizes,
            'overlaps_with_previous_in_chosen_order': overlap_with_previous,
            'gap_to_lambda_times_7077': lam * 7077 - S,
            'family_max_abs_entry': maxA,
            'family_isometry_int64_worst_bound': fam_iso_bound,
            'image_int64_worst_bound': image_bound,
            'group_elems_sha256': sha256_array(gs),
        }

    print('\n5. Exact lifting inequalities')
    # These are the complete pair-type inequalities for the cap construction at t=3/4.
    equator_equator = Fraction(3, 6)  # distinct P48p shell vectors have inner product <= 3 by the minimum-6 premise
    same_class_distinct_heads = T * Fraction(2, 6) + ONE_MINUS_T * 1
    same_line_opposite_tail = T * 1 + ONE_MINUS_T * (-1)
    # Different assigned classes are paired with distinct antipodal tail lines. This
    # injective tail assignment is essential: if two different head classes reused the
    # same tail line, the general cross-class head bound 3/6 would give 5/8, not 1/2.
    different_classes_distinct_tail_lines = T * Fraction(3, 6) + ONE_MINUS_T * Fraction(1, 2)
    different_classes_same_tail_general_bound = T * Fraction(3, 6) + ONE_MINUS_T * 1
    cap_pole = Fraction(1, 2) * 1
    # cap-equator uses sqrt(3)/2 * (3/6) = sqrt(3)/4 < 1/2; compare squares.
    cap_equator_square_left = Fraction(3, 16)
    cap_equator_square_right = Fraction(1, 4)
    require(equator_equator <= Fraction(1, 2), f'equator-equator maximum from the P48p shell: {equator_equator} <= 1/2')
    require(same_class_distinct_heads <= Fraction(1, 2), f'same class/same tail: {same_class_distinct_heads} <= 1/2')
    require(same_line_opposite_tail <= Fraction(1, 2), f'same head line/opposite tail: {same_line_opposite_tail} <= 1/2')
    require(different_classes_distinct_tail_lines <= Fraction(1, 2), f'different assigned classes on distinct tail lines: {different_classes_distinct_tail_lines} <= 1/2')
    require(different_classes_same_tail_general_bound == Fraction(5, 8), 'reusing a tail line for different classes would only have the general bound 5/8 and is not part of this theorem')
    require(cap_pole <= Fraction(1, 2), f'cap-pole maximum: {cap_pole} <= 1/2')
    require(cap_equator_square_left < cap_equator_square_right, 'cap-equator maximum sqrt(3)/4 is strictly below 1/2')

    print('\nSummary')
    print(f'{"dim":>3} {"lambda":>6} {"S":>9} {"tail":>5} {"bound":>12} {"public":>12} {"gain":>7}')
    for dim in range(49, 56):
        r = results[dim]
        print(f'{dim:3d} {r["lambda"]:6d} {r["S"]:9d} {r["tail_points"]:5d} {r["kissing_lower_bound"]:12d} {r["public_comparison"]:12d} {r["strict_gain"]:7d}')

    proof_premises = [
        'The lattice represented by data/P48p.html and p48p_gram.npy is the published P48p extremal even unimodular lattice; this verifier parses P48p.html and checks entrywise equality with the loaded Gram and generator arrays.',
        'P48p has minimal norm 6 and 52,416,000 minimal vectors; the script reads MINIMAL_NORM=6 from the catalogue page and uses the shell count from Leech--Sloane/Cohn table/Sun--Wang as a sourced lattice fact rather than re-enumerating the shell.',
        'For any two distinct P48p minimal lines u,v, |<u,v>| <= 3 follows from the minimal norm: u-v and u+v are nonzero lattice vectors of norms 12-2<u,v> and 12+2<u,v>.',
        'The public comparison values are the 2026-09-23 KR P48 cap package rows for dimensions 49--55, as recorded in the dated comparison table.',
    ]

    cert = {
        'title': '7077-line P48p cap witnesses for dimensions 49--55',
        'status': 'PASS' if not failures else 'FAIL',
        'created_utc': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        'runtime_seconds': time.time() - started,
        'finite_checks': {
            'p48p_html_sha256': sha256_file(cat_html),
            'p48p_gram_sha256': sha256_array(G),
            'p48p_gens_sha256': sha256_array(GE),
            'p48p_gram_bareiss_det': detG,
            'catalogue_minimal_norm_field': cat_min_norm,
            'int64_safety_bounds': {
                'limit': int64_limit,
                'generator_isometry_worst_bound': gen_iso_bound,
                'class_inner_product_worst_bound': class_ip_bound,
            },
            'class_p48_7077_sha256': sha256_array(C),
            'class_size': int(len(C)),
            'class_max_abs_inner_product': max_class_ip,
            'tail_codes': {str(dim): tail_info_by_dim[dim] for dim in sorted(tail_info_by_dim)},
            'used_line_set_hashes_by_dim': used_line_hashes_by_dim,
        },
        'lifting_parameters': {
            'cap_level_t': '3/4',
            'equator_shell_count_premise': N48,
            'delete_two_equator_points_per_used_minimal_line': True,
            'add_four_cap_points_per_used_minimal_line': True,
            'formula': 'N48 - 2*S + 4*S + tau(k) = N48 + 2*S + tau(k)',
            'pair_type_inequalities': {
                'equator_equator': str(equator_equator),
                'same_class_distinct_heads_same_tail': str(same_class_distinct_heads),
                'same_head_line_opposite_tail': str(same_line_opposite_tail),
                'different_assigned_classes_distinct_tail_lines': str(different_classes_distinct_tail_lines),
                'different_classes_same_tail_line_not_allowed_by_general_bound': str(different_classes_same_tail_general_bound),
                'tail_assignment_injective': True,
                'cap_pole': str(cap_pole),
                'cap_equator_squared_comparison': f'{cap_equator_square_left} < {cap_equator_square_right}',
            },
        },
        'published_or_sourced_premises': proof_premises,
        'results': {str(dim): results[dim] for dim in sorted(results)},
        'failures': failures,
    }
    cert_path = args.output
    with open(cert_path, 'w') as f:
        json.dump(cert, f, indent=2, default=int)
    print(f'\nCertificate written to {cert_path}')
    if failures:
        print('\nFAILURES:')
        for msg in failures:
            print(' -', msg)
        return 1
    print('\nALL FINITE CHECKS PASSED; THE SOURCED P48p PREMISES COMPLETE THE LIFTING PROOF.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
