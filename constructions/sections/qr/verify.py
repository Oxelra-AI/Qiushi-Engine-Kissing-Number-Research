"""Reconstruct the archived QR neighbour and certify its minimum via parity.

Literature inputs: the ternary QR [48,24,15] code; its two-symbol
enumerator 1+94*t^24+t^48 after normalizing a full-support word to one.
This performs no short-vector search; output is written to the requested file.
"""
from pathlib import Path
import argparse, ast, json
from sage.all import Matrix, ZZ, QQ, GF, vector as sage_vector

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
from qr_code import qr_code_sage, check_self_dual, sym3, construction_A_basis, solve_mod2, row_hnf_nonzero, lll_rows

code = qr_code_sage()
assert check_self_dual(code)
B0 = construction_A_basis(code)
G0 = B0 * B0.transpose() / 3
diag = [int(G0[i,i]) % 2 for i in range(48)]
c = solve_mod2([[int(G0[i,j]) % 2 for j in range(48)] for i in range(48)], diag)
chi = sage_vector(ZZ, c) * B0
assert all(int(v) % 2 for v in chi)
gamma = [int(chi.dot_product(B0.row(i)) / 3) for i in range(48)]
assert all((gamma[i] - int(G0[i,i])) % 2 == 0 for i in range(48))
i0 = next(i for i in range(48) if gamma[i] % 2)
rows = []
for i in range(48):
    v = [0]*48
    if i == i0:
        v[i] = 2
    else:
        v[i] = 1
        if gamma[i] % 2:
            v[i0] = 1
    rows.append(v)
# Match source order: doubled pivot is the final row.
rows = [v for i,v in enumerate(rows) if i != i0] + [rows[i0]]
C = Matrix(ZZ, rows)
assert abs(C.det()) == 2
H = row_hnf_nonzero([[2*int(v) for v in row] for row in C.rows()] + [c])
B = lll_rows(H * B0)
G = B * B.transpose() / 12
archived = Matrix(ZZ, json.loads((ROOT/'data/gram.json').read_text())['ambient_G'])
assert G == archived, 'Reconstructed and archived Gram matrices differ'
assert G.det() == 1 and G.is_positive_definite()
assert all(v in ZZ for v in G.list()) and all(G[i,i] % 2 == 0 for i in range(48))
s = sage_vector(ZZ, [sym3(int(v)) for v in chi])
assert all(abs(v) == 1 for v in s)
M = Matrix(GF(3), code)
assert M * sage_vector(GF(3), s) == 0
# Normalize coordinates by the full-support codeword s.  Every norm-4
# odd numerator y has y=s*(1-2b), with b a 0/1 word in the normalized code.
# Its weight is 0,24,48 by the stated published code theorem.
# z=(y-chi)/2 must satisfy chi.z=0 mod 6 in the even sublattice.
A = int((chi.dot_product(s) - chi.dot_product(chi)) / 2)
assert all(int(chi[i]*s[i]) % 6 == 1 for i in range(48))
assert A % 6 == 3
assert all((A-w) % 6 == 3 for w in [0,24,48])
payload = {
    'verified': True, 'archived_gram_reproduced_exactly': True,
    'code_rank': int(M.rank()), 'code_self_dual': True,
    'gram_determinant': int(G.det()), 'even': True, 'positive_definite': True,
    'characteristic_squared_length': int(chi.dot_product(chi)),
    'characteristic_dot_full_support': int(chi.dot_product(s)),
    'norm4_parity_residue_mod6': A % 6,
    'minimum_squared_norm': 6,
    'proof': 'Even sector: code minimum 15 excludes norms 2 and 4. Odd sector: all numerator coordinates odd; norm 4 would imply binary weight 0,24,48 and contradict even-sublattice parity. A norm-6 vector is sqrt(3)*(e0+e1).',
    'literature_inputs': ['Extended ternary QR [48,24,15] code', 'Two-symbol enumerator 1+94*t^24+t^48 for the normalized code'],
    'basis_scaled_by_sqrt12': [[int(v) for v in row] for row in B.rows()],
    'characteristic_numerator': [int(v) for v in chi],
    'full_support_residue': [int(v) for v in s],
    'qr_generator': code,
}
args.output.write_text(json.dumps(payload, indent=2))
print(json.dumps({k:v for k,v in payload.items() if k not in ['basis_scaled_by_sqrt12','characteristic_numerator','full_support_residue','qr_generator']}))
