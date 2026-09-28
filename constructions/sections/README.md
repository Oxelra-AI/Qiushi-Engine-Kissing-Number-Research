# Lattice sections and moment certificates

The 43-dimensional package regenerates the projection domain, root orbits,
moment matrix and rational identity from standard $E_8$ coordinates. Its four
inputs specify the ambient Gram matrix, parent section, comparison section
and finite dual certificate.

From `constructions/sections/`, run:

```bash
python d43/verify.py --output /tmp/section43.json
python d43/verify_matrix.py --output /tmp/section43-matrix.json
```

The complete reconstruction uses SymPy. The small matrix checker uses only
Python rational arithmetic and checks the supplied $A^Tw=c$, $w^Tb=2553792$.
The geometric reconstruction explains why those equations apply.

The nested coordinate-section family has a separate exact checker:

```bash
python d43/verify_coordinate_family.py --output /tmp/coordinate-sections.json
```

It constructs eight orbit-moment systems, verifies every rational moment
equation and an explicit full-column-rank minor for each system, and checks
the Weyl map from the original D5 section to the fifth coordinate cut.
The counts are fixed by the embedding; the proof does not require the
ambient lattice to carry the parent Weyl action.

The 45-dimensional proof uses the specified QR neighbour. With a Python
interpreter providing SageMath, run:

```bash
python qr/verify.py --output /tmp/qr-ambient.json
python d45/verify.py --output /tmp/projection45.json
```

The first command reconstructs the ambient Gram matrix and minimum-six
argument. The second checks 298 witnesses, regenerates the section signatures
and verifies the rational moment certificate. Norm-eight section vectors
reduce the complete domain from 239 to 209 signatures. On the 101 remaining
nonexceptional antipodal orbits, the certificate has zero slack and proves
the exact identity $T=7377408+9f(-2,-2,3)$.
The multiplier in `d45/data/dual.json` is checked against the regenerated
signature ordering and all 161 exact moment rows, without solving a numerical
optimization problem.
Its Gram matrix is identical to the input of the ambient reconstruction.

An independent checker uses only Python's standard library:

```bash
python d45/verify_statistics.py --output /tmp/statistics45.json
```

It rebuilds both domains and all rational moments, checks the exact identity,
and obtains the universal anchor-graph counts from degree-eight and
degree-ten spherical moments.

The parent-graph discovery can be reproduced separately with NumPy:

```bash
python d45/verify_parent.py --output /tmp/parent45.json
```

It checks all 2,256 endpoints, their 1,128 pairs $\{x,p-x\}$ centred at
$p/2$, and the eighth-moment count proving completeness. The selected
nonadjacent graph vertices have degree 368 and 70 common neighbours.
The remaining 298 neighbours regenerate exactly the section and fibre
vectors used by `d45/verify.py`. The reverse correspondence checks that
these vectors form the complete target fibre. The moment identity
therefore gives exactly $7377408+9(298)=7380090$ projected points.

The same checker retains the signs of the centred Gram matrix. Integer
identities verify the tight frame and $S^2=88S+368I$, fixing the signed
spectrum and the parity of every common-neighbour count. It enumerates
all 428,076 nonadjacent pairs: the minimum is 70, attained by exactly one
pair. Thus the supplied construction maximizes the projected count for
this anchor and section type. Changing the anchor or its ambient lattice
is a different optimization problem.

The proofs use the stated published code parameters and spherical design
theorems. Neither dimension requires enumeration of the complete
52,416,000-point ambient shell.
