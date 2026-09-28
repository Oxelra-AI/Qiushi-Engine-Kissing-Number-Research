#!/usr/bin/env python3
"""Check the section-count identity and universal anchor moments over Q.

The geometric premises are an extremal even unimodular lattice of rank 48
and section Gram matrix 8I-2J. The QR lattice and its stored embedding are
checked separately. This program uses only Python's standard library.
"""
import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from math import prod
from pathlib import Path


DATA = Path(__file__).resolve().parent / "data"
H = ((6, -2, -2), (-2, 6, -2), (-2, -2, 6))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(y):
    return min(tuple(y), tuple(-v for v in y))


def monomial(y, alpha):
    return prod(v ** a for v, a in zip(y, alpha))


def shell_moment(alpha, gram):
    """Wick pairings for the radius-sqrt(6), rank-48 shell of size 52416000."""
    @lru_cache(None)
    def pairings(degrees):
        if not any(degrees):
            return 1
        i = next(i for i, value in enumerate(degrees) if value)
        remaining = list(degrees)
        remaining[i] -= 1
        total = 0
        for j, multiplicity in enumerate(remaining):
            if multiplicity:
                residual = remaining.copy()
                residual[j] -= 1
                total += multiplicity * gram[i][j] * pairings(tuple(residual))
        return total

    degree = sum(alpha)
    require(degree % 2 == 0 and degree <= 10, "Moment outside the available design degree")
    m = degree // 2
    return Fraction(52416000 * 6 ** m * pairings(tuple(alpha)),
                    prod(48 + 2 * j for j in range(m)))


def signature_domain():
    roots = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))
    exceptional = set()
    for root in roots:
        y = tuple(sum(row[j] * root[j] for j in range(3)) for row in H)
        exceptional.update((y, tuple(-v for v in y)))
    domain = []
    for y in product(range(-6, 7), repeat=3):
        if sum(v*v for v in y) + sum(y)**2 > 48:
            continue
        if y in exceptional or (max(map(abs, y)) <= 3 and abs(sum(y)) <= 3):
            domain.append(y)
    return domain, exceptional


def norm_eight_admissible(y):
    return all(abs(y[i] + y[j]) <= 4 for i, j in combinations(range(3), 2))


def reconstruct():
    domain, exceptional = signature_domain()
    free = sorted({canonical(y) for y in domain if y not in exceptional})
    alphas = [a for a in product(range(11), repeat=3) if sum(a) <= 10 and sum(a) % 2 == 0]
    rows = [[(1 if y == (0, 0, 0) else 2) * monomial(y, a) for y in free] for a in alphas]
    rhs = [shell_moment(a, H) - sum(monomial(y, a) for y in exceptional) for a in alphas]
    targets = {canonical(y) for y in ((1, 0, 0), (0, 1, 0), (0, 0, 1))}
    fibre = canonical((-2, -2, 3))
    target = [int(y in targets) - 9 * int(y == fibre) for y in free]
    return domain, exceptional, free, alphas, rows, rhs, target


def check(data=DATA):
    certificate_path = data / "dual.json"
    saved = json.loads(certificate_path.read_text())
    domain, exceptional, free, alphas, rows, rhs, target = reconstruct()
    require((len(domain), len(exceptional), len(free), len(alphas)) == (239, 8, 116, 161),
            "Original signature system dimensions")
    require(saved["signature_representatives"] == list(map(list, free)), "Signature ordering")
    require(saved["moment_multi_indices"] == list(map(list, alphas)), "Moment ordering")
    require(saved["constant"] == 7377408, "Stored constant")
    require(saved["target"] == "sum_i f(e_i) - 9 f(-2,-2,3)", "Stored target")
    dual = list(map(Fraction, saved["dual"]))
    require(len(dual) == len(alphas) and sum(bool(v) for v in dual) == 107, "Dual length or support")
    constant = sum(w*b for w, b in zip(dual, rhs))
    slack = [Fraction(c) - sum(w*row[j] for w, row in zip(dual, rows))
             for j, c in enumerate(target)]
    require(constant == 7377408 and min(slack) >= 0, "Original rational lower certificate")
    refined = [y for y in domain if norm_eight_admissible(y)]
    active = [j for j, y in enumerate(free) if norm_eight_admissible(y)]
    require(all(norm_eight_admissible(y) for y in exceptional), "Exceptional-fibre subtraction changed")
    require((len(refined), len(active)) == (209, 101), "Refined signature system dimensions")
    require(all(slack[j] == 0 for j in active), "Target is not an exact row combination on the refined domain")
    positive = [{"signature": list(y), "slack": str(s)}
                for y, s in zip(free, slack) if s > 0]
    require(len(positive) == 7, "Positive reduced-cost support")
    require(all(not norm_eight_admissible(entry["signature"]) for entry in positive),
            "A positive reduced cost remains geometrically admissible")

    # p^2=8, q^2=4, p.q=0, with q=r-p/2 for r in A_p.
    anchor_gram = ((8, 0), (0, 4))
    coefficients = {8: 1, 6: -14, 4: 49, 2: -36}
    polynomial_sum = sum(c * shell_moment((degree, 0), anchor_gram)
                         for degree, c in coefficients.items())
    mixed_sum = sum(c * shell_moment((degree, 2), anchor_gram)
                    for degree, c in coefficients.items())
    p_at_four = 16*15*12*7
    endpoint_count = polynomial_sum / (2*p_at_four)
    endpoint_second_moment = mixed_sum / (2*p_at_four)
    degree = (endpoint_second_moment - 32) / 2
    require((endpoint_count, endpoint_second_moment, degree) == (2256, 768, 368),
            "Universal anchor moments")
    return {"passed": True, "original_signatures": len(domain),
            "refined_signatures": len(refined), "refined_free_orbits": len(active),
            "moment_rows": len(alphas), "exact_constant": int(constant),
            "exact_identity": "f(e1)+f(e2)+f(e3)=7377408+9*f(-2,-2,3)",
            "excluded_positive_slacks": positive, "anchor_endpoint_count": int(endpoint_count),
            "anchor_second_moment": int(endpoint_second_moment), "anchor_degree": int(degree),
            "dual_sha256": hashlib.sha256(certificate_path.read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(check(args.data), indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)
    print(result, end="")
