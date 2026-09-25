"""Finite algebra for the specified ternary QR neighbour."""
from sage.all import Matrix, ZZ, QQ, GF, vector as sage_vector

def qr_code_sage():
    # Same mathematical source as ternary_codes.cc: extended ternary QR code.
    # The degree-23 factor choice is equivalent up to code equivalence; exact
    # neighbour selection is later tied to a sourced certificate section.
    F = GF(3); R = F['x']; x = R.gen(); n = 47
    f = sum(x**i for i in range(n))
    g = None
    for poly, mult in f.factor():
        if poly.degree() == 23:
            g = poly; break
    if g is None:
        raise RuntimeError('QR factor not found')
    k = 24
    coeff = [int(c) for c in g.list()] + [0]*(24-len(g.list()))
    G47 = []
    for i in range(k):
        row = [0]*n
        for d, c in enumerate(coeff[:24]):
            row[i+d] = c % 3
        G47.append(row)
    D = [[sum(G47[i][c]*G47[j][c] for c in range(n)) % 3 for j in range(k)] for i in range(k)]
    i0 = next(i for i in range(k) if D[i][i] != 0)
    c0 = 1 if (-D[i0][i0]) % 3 == 1 else 2
    inv = 1 if c0 == 1 else 2
    col = [0]*k; col[i0] = c0
    for j in range(k):
        col[j] = (-D[i0][j]*inv) % 3
    return [G47[i] + [col[i]] for i in range(k)]

def check_self_dual(G):
    M = Matrix(GF(3), G)
    return M.rank() * 2 == M.ncols() and (M*M.transpose()).is_zero()

def sym3(x):
    x %= 3
    return -1 if x == 2 else x

def rref_mod3_rows(G):
    A = [[x % 3 for x in row] for row in G]
    m = len(A); n = len(A[0]); row = 0; pivots = []
    for col in range(n):
        piv = None
        for r in range(row, m):
            if A[r][col] % 3:
                piv = r; break
        if piv is None:
            continue
        A[row], A[piv] = A[piv], A[row]
        inv = 1 if A[row][col] == 1 else 2
        A[row] = [(inv*x) % 3 for x in A[row]]
        for r in range(m):
            if r != row and A[r][col] % 3:
                fac = A[r][col] % 3
                A[r] = [(A[r][c] - fac*A[row][c]) % 3 for c in range(n)]
        pivots.append(col); row += 1
        if row == m:
            break
    rows = [[sym3(x) for x in A[i]] for i in range(row)]
    return rows, pivots

def construction_A_basis(G):
    rows, pivots = rref_mod3_rows(G)
    if len(rows) != 24:
        raise RuntimeError(f'code rank after RREF {len(rows)}')
    nonpiv = [j for j in range(48) if j not in set(pivots)]
    B = [list(r) for r in rows]
    for j in nonpiv:
        v = [0]*48; v[j] = 3; B.append(v)
    B = Matrix(ZZ, B)
    if B.nrows() != 48 or abs(int(B.det())) != 3**24:
        raise RuntimeError('bad Construction-A basis determinant')
    Gint = B*B.transpose()
    for i in range(48):
        for j in range(48):
            if int(Gint[i,j]) % 3:
                raise RuntimeError('Construction-A Gram not divisible by 3')
    return B

def solve_mod2(A, b):
    F = GF(2)
    return [int(x) for x in Matrix(F, A).solve_right(sage_vector(F, b))]

def row_hnf_nonzero(rows):
    M = Matrix(ZZ, rows)
    H = M.hermite_form()
    out = []
    for i in range(H.nrows()):
        row = [int(H[i,j]) for j in range(H.ncols())]
        if any(row):
            out.append(row)
    return Matrix(ZZ, out)

def lll_rows(M):
    try:
        return M.LLL()
    except Exception:
        return M
