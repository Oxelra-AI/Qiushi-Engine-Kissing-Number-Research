"""Check the exact reductions from the Pless code to the specified mother shell.

The minimum-distance and complete-weight-enumerator theorems are the published
inputs identified below. This checks their coordinate match, the neighbour
arithmetic, and the theta-series calculation, not a new enumeration of 3**24 words.
"""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def paley():
    squares = {x*x % 23 for x in range(1, 23)}
    matrix = [[0]*24 for _ in range(24)]
    for j in range(1, 24):
        matrix[0][j], matrix[j][0] = 1, -1
    for i in range(1, 24):
        for j in range(1, 24):
            if i != j:
                matrix[i][j] = 1 if (i-j) % 23 in squares else -1
    return matrix


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b, degree=3):
    return [sum(a[i]*b[k-i] for i in range(k+1)
                if i < len(a) and k-i < len(b)) for k in range(degree+1)]


def power(a, n, degree=3):
    result = [1] + [0]*degree
    for _ in range(n):
        result = multiply(result, a, degree)
    return result


def theta_coefficients():
    e4 = [1] + [240*sum(d**3 for d in range(1, n+1) if n % d == 0)
                for n in range(1, 4)]
    delta = [0, 1, -24, 252]
    a, b, c = power(e4, 6), multiply(power(e4, 3), delta), power(delta, 2)
    return [x-1440*y+125280*z for x, y, z in zip(a, b, c)]


def check(matrix=None, characteristic=None, glue=None, root=ROOT):
    s = matrix if matrix is not None else paley()
    c = characteristic if characteristic is not None else [1]*24 + [-23] + [1]*23
    g = glue if glue is not None else [c[0]+6] + c[1:]
    require(s == paley(), 'The matrix must match the cited Pless C(23) convention')
    require(c == [1]*24 + [-23] + [1]*23, 'Characteristic coordinate convention')
    require(g == [c[0]+6] + c[1:], 'The specified even neighbour is required')
    require(all(dot(s[i], s[j]) == (23 if i == j else 0)
                for i in range(24) for j in range(24)), 'Paley orthogonality')
    require(all(s[i][j] == -s[j][i] for i in range(24) for j in range(24)), 'Skew symmetry')
    basis = [[int(i == j) for j in range(24)] + s[i] for i in range(24)]
    basis += [[0]*24 + [3*int(i == j) for j in range(24)] for i in range(24)]

    def in_code(row):
        return all((sum(row[i]*s[i][j] for i in range(24))-row[24+j]) % 3 == 0
                   for j in range(24))

    require(in_code([1]*48) and in_code(c) and in_code(g), 'Code membership')
    require(all(dot(x, y) % 3 == 0 for x in basis for y in basis), 'Integral lattice')
    require(all((dot(c, x)-dot(x, x)) % 6 == 0 for x in basis), 'Characteristic congruence')
    require(dot(g, g) == 624 and dot(g, g) % 24 == 0, 'Even glue norm')
    # The written neighbour is the standard all-one neighbour, in the same coordinates.
    canonical = [7]+[1]*47
    shift = [(a-b)//2 for a, b in zip(g, canonical)]
    require(all((a-b) % 2 == 0 for a, b in zip(g, canonical)), 'Integral neighbour shift')
    require(in_code(shift) and dot(shift, shift) % 6 == 0, 'Same even-neighbour coset')

    # An explicit Hadamard matrix in this very code, independently of naming conventions.
    h = []
    for i in range(24):
        a = [int(i == j)+s[i][j] for j in range(24)]
        b = [int(i == j)-s[i][j] for j in range(24)]
        h.append(a+a)
        h.append(b+[-x for x in b])
    require(all(set(row) <= {-1, 1} and in_code(row) for row in h), 'Hadamard codewords')
    require(all(dot(h[i], h[j]) == (48 if i == j else 0)
                for i in range(48) for j in range(48)), 'Hadamard orthogonality')
    full_words = h + [[-x for x in row] for row in h]
    signs = Counter(sum(x == -1 for x in row) for row in full_words)
    require(signs == {0: 1, 24: 94, 48: 1}, 'Full-support sign distribution')
    # For y in {+1,-1}^48, z=(y-g)/2, c.z == 3-w (mod 6).
    require((sum(c)-dot(c, g)) % 12 == 6 and all(x % 6 == 1 for x in c),
            'Odd-coset norm-four congruence')
    require(all((3-w) % 6 != 0 for w in signs), 'Exclusion of norm four in the odd coset')
    # Norm six is attained already in the even sublattice.
    example = [3, 3]+[0]*46
    require(in_code(example) and dot(example, example) == 18, 'Norm-six witness')
    theta = theta_coefficients()
    require(theta == [1, 0, 0, 52416000], 'Theta-series coefficient')

    finite_path = root/'evidence/p48-finite-verification.json'
    if finite_path.exists():
        finite = json.loads(finite_path.read_text())
        require(finite['chi'] == c and finite['glue'] == g, 'Finite checker uses a different neighbour')
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return dict(valid=True, code='Pless C(23)', dimension=48,
                checked=['exact Pless generator convention', 'integrality and characteristic vector',
                         'even-neighbour coset identity', 'Hadamard codeword identities',
                         'norm-four parity exclusion', 'norm-six witness', 'theta coefficients'],
                published_inputs=[
                    dict(result='C(23) has minimum Hamming weight 15',
                         source='Pless (1972); Tonchev (2022), Section 1',
                         url='https://arxiv.org/abs/2109.05514'),
                    dict(result='Complete weight enumerator restricted to two symbols has weights 0,24,48',
                         source='Munemasa--Tamura (2012), equation (20)',
                         url='https://arxiv.org/abs/1006.2414')],
                full_support_negative_weights=dict(sorted(signs.items())),
                characteristic=c, glue=g, theta_coefficients=theta,
                ambient_minimum_squared=6, shell_size=52416000,
                proof_basis='Published code theorems, short-vector exclusion, and modular theta series',
                proof_section='paper/sections/p48.tex', checker_sha256=source_hash)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'evidence/p48-ambient.json')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(valid=False))+'\n')
    result = check()
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
