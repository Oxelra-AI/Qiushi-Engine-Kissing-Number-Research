# Mathematical paper

**Large-Scale Autonomous Discovery of Kissing Number Constructions**

[Read the paper (PDF)](main.pdf) · [LaTeX source](main.tex)

The paper presents Qiushi Engine's autonomous investigation of kissing
numbers in dimensions 25, 27, 32–39, 43, 45 and 49–55. It asks how changing
the mathematical representation of a constrained configuration can reveal
new constructions, and develops the geometric and combinatorial statements
that establish the resulting bounds.

Coordinated motion and labelled lifting control how retained and added
points interact. Joint exchanges share deletion costs, while signed-design
transfers yield larger local replacements and a sharp capacity bound.
Cross-shell compatibility and unions of isometric line classes give further
extensions. For lattice sections, moment identities determine a target count
and moment inequalities turn small fibre witnesses into a much larger lower
bound. The E8-extension theorem applies to every extremal even unimodular
lattice of rank 48 containing the specified embedded root system.

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

The complete finite data and verification programs are also available as
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
