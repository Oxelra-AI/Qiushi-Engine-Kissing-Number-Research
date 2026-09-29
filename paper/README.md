# Mathematical paper

**Large-Scale Autonomous Discovery of Kissing Number Constructions**

Preprint: [arXiv:2609.35051](https://arxiv.org/abs/2609.35051) · [arXiv PDF](https://arxiv.org/pdf/2609.35051) · [BibTeX](../CITATION.bib).
Version 1 was submitted on 28 September 2026, under Information Theory (cs.IT).

[Read the paper (PDF)](main.pdf) · [LaTeX source](main.tex)

The paper presents Qiushi Engine's autonomous investigation of kissing
numbers in dimensions 25, 27, 32–39, 43, 45 and 49–55. It asks how changing
the mathematical representation of a constrained configuration can reveal
new constructions, and develops the geometric and combinatorial statements
that establish the resulting bounds.

Coordinated motion and labelled lifting control how retained and added
points interact. Joint exchanges share deletion costs, while signed-design
transfers yield a parameterized family of local signed codes and a sharp
capacity bound. A shell-norm window guarantees cross-compatibility, while
orbitwise coverage bounds control unions of isometric line classes.
For lattice sections, the E8-extension theorem fixes the 43-dimensional
count across all extremal even unimodular lattices of rank 48 containing
the specified embedded root system. In dimension 45, a second identity
determines the projected count from a single fibre, represented exactly
by a neighbourhood difference in a 1128-vertex, 368-regular graph.

## Construction principles

The dimensions share mathematical inputs and principles rather than
requiring a separate method for every entry of the result table.

| Dimensions | Structural question | Results developed in the paper |
|---|---|---|
| 25 | Which boundary changes allow a Gram-preserving motion? | A finite circle–half-plane test; necessity and sufficiency of the two cap repairs in the specified motion family. |
| 27 | How often can a head direction be reused? | A labelled lifting criterion, incidence capacities, and a sharp simplex criterion coupling head separation to tail dimension. |
| 32–34, 37, 39 | When do several insertions jointly pay for their blockers? | Shared-deletion optimization and an exact maximum-matching certificate for compatible candidate pools. |
| 35–37 | Which signed replacements fit the retained boundary? | A sharp infinite transverse family and an exact capacity formula for the twelve-coordinate, complete-type transverse 2+2 model; the fixed 37-dimensional boundary attains 512 in this model. |
| 38 | When are new shells compatible with an entire lifted shell? | An automatic cross-shell window, a multi-shell separation criterion, endpoint-contact counts and exclusion of the next shell for the fixed base. |
| 43 | Can an embedded parent determine a child section's population? | One polynomial determines eight nested coordinate-section counts, including the specified D5 count, independently of the ambient extremal lattice. |
| 45 | Which geometric data determine a projected count? | An exact fibre identity, anchor-graph reduction, signed spectrum and the complete fixed-anchor optimum for the specified section Gram. |
| 49–55 | What freedom remains in antipodal block lifting? | Rigidity of paired latitudes; exact reduction to image coverage; orbitwise and finite-pool selection guarantees. |

The [rational statistics checker](../constructions/sections/d45/verify_statistics.py)
reconstructs the refined signature domain, count identity and universal
anchor moments using only Python's standard library. The
[parent checker](../constructions/sections/d45/verify_parent.py) establishes
the complete 298-point fibre, verifies the signed-frame identities, and
enumerates all 428,076 nonadjacent pairs of the supplied anchor graph.
The [motion checker](../constructions/d25/verify_motion_obstructions.py)
certifies the two necessary cap changes; the
[contact checker](../constructions/d38/verify_contacts.py) checks all 144
endpoint contact layers. The
[finite-pool selector](../constructions/p48/coverage.py) uses exact integer
scores and rational conditional expectations.
The [boundary solver](../constructions/codes/hadamard/boundary.py) returns
optimal source families for a fixed pairing and a fixed 2+2 division of
twelve coordinates, together with matching and vertex-cover certificates;
the tests cover all 512 complete-type boundaries.
The [coordinate-section checker](../constructions/sections/d43/verify_coordinate_family.py)
reconstructs the eight exact moment systems and their full-rank minors,
then checks the Weyl correspondence with the original D5 section.

The opening table gives all nineteen bounds, their public comparisons and
increases. The introduction and the autonomous-research section describe
Qiushi Engine's contribution.

The appendices give the Golay/Leech convention, binary generators, the
explicit Pless neighbour and local deformation arguments. The finite
inputs remain in [`constructions/`](../constructions/), linked to the
[verification tasks](../evidence/proof-map.md).

Compile from the repository root with XeLaTeX and BibTeX:

```sh
make paper
```

The PDF is written to `paper/main.pdf`; intermediate files stay in `build/paper/`.

To compile directly from this directory, or from an extracted paper source
archive, run:

```sh
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

This produces `main.pdf` in the current directory. The required packages
are listed in `preamble.tex`; BibTeX supplies the numbered references.

The finite inputs for the nineteen numerical constructions are also available as
[a separate certificate archive](../reports/en_full/certificates.zip),
identical to the attachment in both complete reports. Its README gives
the commands for checking each construction.

From the repository root, `make source-paper` creates
`dist/kissing-number-paper-source.zip`. This archive puts `main.tex` at
the compilation root and includes only its active source files and bibliography.
Construction data and verification programs remain in the separate certificate
archive linked above; they are not included in the paper source ZIP.

The [bilingual reports](../reports/README.md) give the construction arguments
together with the research development. [Verification instructions](../reproducibility/README.md)
connect the finite inputs to the exact checks.
