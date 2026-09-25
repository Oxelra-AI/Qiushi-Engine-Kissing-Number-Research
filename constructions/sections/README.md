# Lattice sections and moment certificates

The 43-dimensional package regenerates the projection domain, root orbits,
moment matrix and rational identity from standard $E_8$ coordinates. Its four
inputs specify the ambient Gram matrix, parent section, comparison section
and finite dual certificate.

```bash
python d43/verify.py --output /tmp/section43.json
python d43/verify_matrix.py --output /tmp/section43-matrix.json
```

The complete reconstruction uses SymPy. The small matrix checker uses only
Python rational arithmetic and checks the supplied $A^Tw=c$, $w^Tb=2553792$.
The geometric reconstruction explains why those equations apply.

The 45-dimensional proof uses the specified QR neighbour. With a Python
interpreter providing SageMath, run:

```bash
python qr/verify.py --output /tmp/qr-ambient.json
python d45/verify.py --output /tmp/projection45.json
```

The first command reconstructs the ambient Gram matrix and minimum-six
argument. The second checks 298 witnesses, regenerates all section signatures
and verifies the rational inequality giving $7377408+9(298)=7380090$.
The multiplier in `d45/data/dual.json` is checked against the regenerated
signature ordering and all 161 exact moment rows, without solving a numerical
optimization problem.
Its Gram matrix is identical to the input of the ambient reconstruction.

The parent-graph discovery can be reproduced separately with NumPy:

```bash
python d45/verify_parent.py --output /tmp/parent45.json
```

It checks all 2,256 endpoints, their 1,128 pairs $\{x,p-x\}$ centred at
$p/2$, and the eighth-moment count proving completeness. The selected
nonadjacent graph vertices have degree 368 and 70 common neighbours.
The remaining 298 neighbours regenerate exactly the section and fibre
vectors used by `d45/verify.py`.

The proofs use the stated published code parameters and spherical design
theorems. Neither dimension requires enumeration of the complete
52,416,000-point ambient shell.
