# A 197580-point kissing configuration in dimension 25

**Result:** \(K(25)\ge197580\). The construction and its finite certificate were verified on 26 September 2026.

Starting from the [public 197579-point configuration](https://github.com/alexlegeartis/KissingNumbers/tree/cf14c5ef4db6059bbf2e570e3f0ce24edfda243e/verifications/improved/dim25-lens-heads), move 552 retained Leech-shell points together, add one point, and replace two cap points. The point count increases by one. The original head coordinates and the baseline construction are credited to the linked source.

## The geometric change

Use squared norm 4 and pairwise inner product at most 2. Let \(v\) be the baseline's first norm-6 direction and \(n=v/\sqrt6\). Its 552 removed shell points \(u\) have retained partners \(w=u+v\). Write

\[
w=r+\sqrt{3/2}\,n,\qquad r\perp n.
\]

Move each \((w,0)\) to \((r+an,b)\), where

\[
a=\frac{\sqrt3}{2}+\frac{\sqrt2}{4},\qquad
b=\frac{\sqrt6-2}{4}.
\]

Since \(a^2+b^2=3/2\), these 552 points retain their norms and mutual inner products. Their horizontal components are convex combinations of \(u\) and \(w\), so they remain compatible with every unmoved retained shell point. The motion makes room for

\[
Q=(\sqrt3n,-1),\qquad Q\cdot(r+an,b)=2.
\]

Two old cap points must be replaced. The replacements are \(2k/\sqrt{1007176}\) and \(2\ell/\sqrt{10209}\), with small integer vectors in [repair-points.json](repair-points.json). All remaining comparisons have strict margins and pass integer or rigorous interval checks.

The complete proof, including both integer vectors, is [construction.tex](construction.tex).

## Reproduce

From this directory, using Python with the versions in `requirements.txt`:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B verify.py
```

The last line is:

```text
PASS: 197580 distinct points in dimension 25; squared norm 4; pair products <= 2.
```

The verifier reconstructs the Leech minimal shell from the Golay code. It checks the inherited baseline with integer and rational arithmetic, then checks the extension with integer arithmetic and 192-bit Arb enclosures. The shell's mutual compatibility follows from the Leech lattice minimum; the proof covers all new equality cases algebraically. The check runs offline and does not use an optimization solver.

For a recorded replay, including rejection of two incompatible replacements,
run from the repository root:

```sh
python3 tools/verify_dimension25.py --rejections --output ../dimension25-verification.json
```

Both commands leave the input files unchanged.

| File | Contents |
|---|---|
| `baseline-heads.json` | Exact original head coordinates, owners, direction, source and hashes |
| `repair-points.json` | Two new integer vectors and their exact normalization |
| `construction.tex` | Mathematical construction and proof |
| `verify_baseline.py` | Independent exact check of the inherited configuration |
| `verify_extension.py` | Strict check of every new type of comparison |
| `verify.py` | Complete verification entry |
| `verification.json` | Complete verification result, including the baseline and extension |
| `export.py` | Reconstruct all coordinates as a numerical array |
| `golay.py`, `leech.py` | Source-attributed shell enumeration |

The Golay/Leech enumeration and inherited data come from the pinned source above. Its license is preserved in `THIRD_PARTY_LICENSE.txt`. This directory contains the editable proof and reproducible certificate; no PDF is needed.
