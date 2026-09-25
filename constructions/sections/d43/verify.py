#!/usr/bin/env python3
"""Regenerate the 43-dimensional proof from standard E8 coordinates.

Published inputs: the CQ48a/P48n lattice has minimum squared norm 6 and
52,416,000 minimal vectors; its minimal shell is an 11-design (Venkov).
All remaining identities, finite domains, moments and counts are checked here.
"""
import argparse
import ast
from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import re
import time

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
CERT = DATA / 'certificate.json'
PARENT = DATA / 'parent-section.txt'
OLD = DATA / 'comparison-section.txt'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rows(text, marker, n, m):
    lines = text.splitlines()
    i = next(i for i, line in enumerate(lines) if line.startswith(marker)) + 1
    out = [[int(x) for x in re.findall(r'-?\d+', line)] for line in lines[i:i+n]]
    require(len(out) == n and all(len(r) == m for r in out), marker)
    return sp.Matrix(out)


def ambient():
    raw = (DATA / 'CQ48a.html').read_text()
    block = raw.split('<a NAME="GRAM">')[1].split('<a NAME="DIVISORS">')[0]
    text = re.sub(r'<[^>]*>', '\n', block)
    rr = [[int(x) for x in line.split()] for line in text.splitlines()
          if re.fullmatch(r'\s*-?\d+(?:\s+-?\d+)*\s*', line)]
    require(rr.pop(0) == [48, 0], 'catalogue header')
    require(len(rr) == 48 and all(len(r) == i+1 for i, r in enumerate(rr)), 'Gram shape')
    G = sp.zeros(48)
    for i, r in enumerate(rr):
        for j, x in enumerate(r):
            G[i, j] = G[j, i] = x
    source = PARENT.read_text()
    require(G == rows(source, 'ambient Gram G', 48, 48), 'catalogue mismatch')
    T = rows(source, 'coefficient rows w.r.t.', 8, 48)
    B = rows(source, 'section basis rows B', 8, 48)
    H = rows(source, 'section Gram K', 8, 8)
    require(T * G * T.T == H == B * B.T / 96, 'actual embedding')
    require(G.det() == 1 and H.det() == 6561, 'determinants')
    # Exact rational LDL; avoids repeated symbolic principal-minor queries.
    from fractions import Fraction
    ld = [[Fraction(int(G[i, j])) for j in range(48)] for i in range(48)]
    for k in range(48):
        pivot = ld[k][k]
        require(pivot > 0, 'positive definite ambient')
        for i in range(k+1, 48):
            for j in range(i, 48):
                ld[j][i] -= ld[i][k]*ld[j][k]/pivot
                ld[i][j] = ld[j][i]
    require(all(int(G[i, i]) % 2 == 0 for i in range(48)), 'even ambient')
    for C in (T, T[:5, :]):
        S = smith_normal_form(C, domain=sp.ZZ)
        require(all(abs(S[i, i]) == 1 for i in range(C.rows)), 'primitive section')
    require((T[:5, :] * G * T[:5, :].T).det() == 972, 'D5 determinant')
    bad = T.copy(); bad[0, 0] += 1
    require(bad * G * bad.T != H, 'negative control: changed embedding')
    old = OLD.read_text()
    require(re.search(r'^kissing = 2545056\b', old, re.M), 'old comparison count')
    old_h = rows(old, 'section Gram K', 5, 5)
    old_g = rows(old, 'ambient Gram G', 48, 48)
    old_t = rows(old, 'coefficient rows w.r.t.', 5, 48)
    require(old_t*old_g*old_t.T == old_h, 'old actual embedding')
    old_s = smith_normal_form(old_t, domain=sp.ZZ)
    require(all(abs(old_s[i, i]) == 1 for i in range(5)), 'old primitive D5')
    require(any(all(old_h[p[i], p[j]] == H[i, j] for i in range(5) for j in range(5))
                for p in itertools.permutations(range(5))), 'old/new isometric D5 forms')
    return H


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def simple_roots():
    # Doubled coordinates, with the exact numbering used by the source Gram.
    rr = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)]
    for i in range(6):
        r = [0]*8; r[i] = -2; r[i+1] = 2; rr.append(tuple(r))
    return rr


def root_set():
    rr = set()
    for i, j in itertools.combinations(range(8), 2):
        for a, b in itertools.product((-2, 2), repeat=2):
            r = [0]*8; r[i] = a; r[j] = b; rr.add(tuple(r))
    for r in itertools.product((-1, 1), repeat=8):
        if sum(x < 0 for x in r) % 2 == 0:
            rr.add(r)
    require(len(rr) == 240, 'E8 roots')
    return rr


def admissible_domain():
    """Exhaust u/2 in E8, ||u||^2<=72, |u.r|<=12 for doubled roots r.

    Pair roots imply the two largest |u_i| sum to <=6. Half roots imply
    L1(u)<=18: their maximum is L1, or L1-2*min|u_i|, and min|u_i|<=3.
    These proven pruning bounds do not assume the answer's shell counts.
    """
    out = set()
    for values in (range(-6, 7, 2), range(-5, 6, 2)):
        def visit(prefix, square, l1, largest, second):
            if len(prefix) == 8:
                if sum(prefix) % 4:
                    return
                maximum = l1
                if all(prefix) and sum(x < 0 for x in prefix) % 2:
                    maximum -= 2*min(abs(x) for x in prefix)
                if maximum <= 12:
                    out.add(tuple(prefix))
                return
            for x in values:
                a = abs(x)
                top, nxt = (a, largest) if a >= largest else (largest, max(second, a))
                if square+x*x <= 72 and l1+a <= 18 and top+nxt <= 6:
                    visit(prefix+[x], square+x*x, l1+a, top, nxt)
        visit([], 0, 0, 0, 0)
    return out


def reflect(u, r):
    p = dot(u, r)
    require(p % 4 == 0, 'integral root pairing')
    return tuple(x-(p//4)*y for x, y in zip(u, r))


def orbits(domain, generators, negative=False):
    left = set(domain); result = []
    while left:
        seed = min(left); left.remove(seed); todo = [seed]; orb = [seed]
        while todo:
            u = todo.pop()
            images = [reflect(u, r) for r in generators]
            if negative:
                images.append(tuple(-x for x in u))
            for v in images:
                require(v in domain, 'domain not closed under reflection')
                if v in left:
                    left.remove(v); todo.append(v); orb.append(v)
        result.append(orb)
    return result


def check():
    start = time.monotonic()
    H = ambient()
    simple = simple_roots(); roots = root_set()
    require(all(r in roots for r in simple), 'simple roots present')
    require(H == sp.Matrix([[3*sp.Rational(dot(a, b), 4) for b in simple] for a in simple]), 'E8 numbering')
    domain0 = admissible_domain()
    shell_counts = dict(sorted(Counter(dot(u, u)//4 for u in domain0).items()))
    require(shell_counts == {0: 1, 2: 240, 4: 2160, 6: 6720, 8: 17280}, 'admissible shells')
    actual_roots = {tuple(3*x for x in r) for r in roots}
    require(not domain0 & actual_roots, 'root exception separated')
    domain = domain0 | actual_roots
    a3 = [r for r in roots if all(dot(r, s) == 0 for s in simple[:5])]
    require(len(a3) == 12, 'D5 perpendicular A3')
    signature = lambda u: tuple(dot(u, r)//4 for r in simple)
    require(all(dot(u, r) % 4 == 0 for u in domain for r in simple), 'integer signatures')
    groups = orbits(domain, simple[:5]+a3, negative=True)
    oo = sorted([sorted(signature(u) for u in O) for O in groups], key=lambda O: (len(O), O[0]))
    require(len(oo) == 43, 'subgroup orbit count')
    root_signatures = {signature(u) for u in actual_roots}
    hi = H.inv()
    cert = json.loads(CERT.read_text())
    metadata = []
    for i, O in enumerate(oo):
        # Norm is constant on each subgroup orbit.
        y = sp.Matrix(O[0]); q = str((y.T*hi*y)[0])
        metadata.append({'orbit': i, 'size': len(O), 'representative': list(O[0]),
                         'q_hist': {q: len(O)}, 'actual_section_root_signatures': sum(y in root_signatures for y in O),
                         'target_signatures': sum(not any(y[:5]) for y in O)})
    require(metadata == cert['orbit_metadata'], 'independent orbit metadata')

    @lru_cache(None)
    def gaussian(alpha):
        if not any(alpha):
            return sp.Integer(1)
        i = next(i for i, a in enumerate(alpha) if a)
        residual = list(alpha); residual[i] -= 1
        total = 0
        for j, a in enumerate(residual):
            if a:
                beta = residual.copy(); beta[j] -= 1
                total += a*H[i, j]*gaussian(tuple(beta))
        return total

    def moment(alpha):
        degree = sum(alpha)
        require(degree <= 10 and degree % 2 == 0, '11-design degree')
        m = degree//2
        denominator = sp.prod(48+2*j for j in range(m))
        return sp.Rational(52416000*6**m, denominator)*gaussian(alpha)

    AA, bb = [], []
    for label in cert['row_labels']:
        if label.startswith('fix_root_orbit_'):
            i = int(label.rsplit('_', 1)[1])
            require(all(y in root_signatures for y in oo[i]), 'fixed root orbit really is root')
            AA.append([int(j == i) for j in range(len(oo))]); bb.append(sp.Integer(1))
        else:
            require(label.startswith('alpha='), 'row label')
            alpha = ast.literal_eval(label[6:])
            terms = [(i, a) for i, a in enumerate(alpha) if a]
            AA.append([sum(math.prod(y[i]**a for i, a in terms) for y in O) for O in oo])
            bb.append(moment(alpha))
    A, b = sp.Matrix(AA), sp.Matrix(bb)
    c = sp.Matrix([m['target_signatures'] for m in metadata])
    require(A == sp.Matrix(cert['A_rows']), 'regenerated A')
    require(b == sp.Matrix([sp.Rational(x) for x in cert['b_rhs']]), 'regenerated b')
    require(c == sp.Matrix(cert['target_c']), 'regenerated c')
    w = sp.Matrix([sp.Rational(x) for x in cert['dual_w']])
    require(A.T*w == c, 'dual identity')
    count = (w.T*b)[0]
    require(count == 2553792, '43D exact count')
    altered = w.copy(); altered[0] += 1
    require(A.T*altered != c, 'negative control: altered dual')

    # A second argument averages over the full E8 Weyl group.
    full = orbits(domain0, simple)
    full_counts = sorted((dot(O[0], O[0])//4, len(O)) for O in full)
    require(full_counts == sorted(shell_counts.items()), 'one Weyl orbit per admissible norm')
    q = [sp.Rational(n, 3) for n in shell_counts]
    M = sp.Matrix([[shell_counts[n]*r**j for n, r in zip(shell_counts, q)] for j in range(5)])
    rhs = lambda j: 52416000*6**j*sp.rf(4, j)/sp.rf(24, j)-240*6**j
    averages = M.inv()*sp.Matrix([rhs(j) for j in range(5)])
    require(sum(shell_counts[n]*r**5*a for n, r, a in zip(shell_counts, q, averages)) == rhs(5), 'unused tenth moment')
    target_counts = Counter(dot(u, u)//4 for u in domain0 if all(dot(u, r) == 0 for r in simple[:5]))
    target_roots = sum(all(dot(u, r) == 0 for r in simple[:5]) for u in actual_roots)
    average_total = target_roots + sum(target_counts[n]*a for n, a in zip(shell_counts, averages))
    require(average_total == count and target_roots == 12, 'independent average argument')
    return {'passed': True, 'dimension': 43, 'lower_bound': int(count), 'comparison': 2545056,
            'increase': int(count)-2545056, 'ambient_catalogue_match': True,
            'old_comparison_certificate_count': 2545056, 'old_new_D5_forms_permutation_isometric': True,
            'parent_and_child_primitive': True, 'child_determinant': 972,
            'admissible_domain_size': len(domain0), 'full_domain_size': len(domain),
            'admissible_shell_counts': shell_counts, 'subgroup_orbits': len(oo),
            'regenerated_matrix_shape': list(A.shape), 'regenerated_A_b_c_match': True,
            'exact_dual_identity': True, 'fixed_child_exact_count': int(count),
            'Weyl_average_fiber_weights': [str(a) for a in averages],
            'target_shell_counts': dict(sorted(target_counts.items())), 'target_actual_roots': target_roots,
            'independent_Weyl_average_count': int(average_total), 'unused_tenth_moment_pass': True,
            'negative_controls': {'changed_embedding_rejected': True, 'changed_dual_rejected': True},
            'published_inputs': ['CQ48a/P48n minimum squared norm 6 and shell size 52416000', 'Venkov 11-design theorem'],
            'full_ambient_shell_enumerated': False, 'imports_session_code': False,
            'certificate_sha256': hashlib.sha256(CERT.read_bytes()).hexdigest(),
            'python': platform.python_version(), 'sympy': sp.__version__,
            'runtime_seconds': round(time.monotonic()-start, 3)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path)
    args = parser.parse_args(); result = check(); text = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(text)
    print(text, end='')
