# Reproducing the results

The reports give the geometric proofs; the verification programs check their
finite inputs. All construction data are included.

## Mathematical verification

Use Python 3.10 or later with NumPy, SymPy and python-flint. The QR-neighbour and
45-dimensional moment checks also require SageMath. The independent code
checker requires a C++17 compiler, selected by `CXX` or `c++`.

Activate a Python environment providing these libraries:

```sh
python3 -c 'import numpy, sympy, flint; from sage.all import QQ'
c++ --version
make list
make verify
```

By default, results are written to a new timestamped directory beside the
repository. If SageMath is installed in a separate environment, set `PYTHON`
to that environment's Python executable. To choose the interpreter or output directory:

```sh
make verify PYTHON=/path/to/sage-environment/bin/python OUTPUT=../kissing-verification
python3 tools/reproduce.py --suite hadamard35-36 --output ../signed-verification
```

The runner copies its inputs, uses one BLAS/OpenMP thread and produces per-job
logs and JSON results. Run Python without optimization: some mathematical checks
use assertions. A completed replay records elapsed times, software versions,
input identities and whether every check passed.

| Construction | Checks |
|---|---|
| Coordinated motion in dimension 25 | Exact baseline, moving-layer identities, interval bounds and two repaired caps |
| Two-layer Leech lifting | Deletion sets, head products, tail labels and the 311-owner selection |
| Layered codes | Generator ranks, code distances, support intersections and exact exchanges |
| Signed replacements | Regeneration of Hadamard images and all boundary products |
| Equatorial completion | Leech shell, tail data, rational rotation and added lines |
| Lattice sections | Ambient lattice, complete signature domains, moment identities and witnesses |
| P48p liftings | Catalogue basis, 7,077-line class, automorphisms, seven image unions and tail ranks |

The exact job list is in [replay_plan.json](../tools/replay_plan.json).
[Recorded verification](../evidence/verification.json) accompanies the data.
[Sources and permissions](../constructions/third-party.md) identify the inputs
used from earlier work.

## Research calculations

### The 25-dimensional motion

The baseline uses exact integer and rational checks; the extension uses
symbolic identities and 192-bit Arb enclosures. Install `python-flint`
alongside NumPy for this check. Both deliberately incompatible repairs
must be rejected.

```sh
python3 tools/reproduce.py --suite dimension25 --output ../check-d25
```

The [construction directory](../constructions/d25/) contains the complete
coordinate prescription and proof. `export.py` generates a numerical
coordinate array for inspection; acceptance uses the exact/interval verifier.

### The 27-dimensional candidate graph

```sh
python3 tools/reproduce.py --suite dimension27 --output ../check-d27
python3 constructions/d27/search.py --output ../d27-candidates
```

The first command verifies the construction. The second reconstructs
the 3,125 candidates and 261,474 conflict edges and checks the 311-owner
selection. Its [saved summary](../research/data/d27-search.json) identifies
the graph. Add `--seconds 600` to search with the optional OR-Tools package;
`--workers` and `--seed` control that search. Search output goes to a new
directory and never replaces the supplied witness.

### The seven P48p liftings

```sh
python3 tools/reproduce.py --suite p48-current --output ../check-p48
python3 constructions/p48/search.py --output ../p48-unions
```

The first command checks the full lifting proof and its finite inputs.
The second checks the eight added lines, reconstructs the chosen image
unions and separates the gain from class enlargement and image selection.
Compare its output with [the saved calculation](../research/data/p48-search.json).
Optional `--images 500 --starts 50 --seed 42 --word-length 30` regenerates
an image pool and performs independent family searches. The reconstruction
uses exact coordinate identities for union counts.

The [regional census](../research/data/support-regions.json) records how much
local freedom remains in the 32- and 37-dimensional support families. Recompute
its triangle counts, largest free-support counts and maximizing regions with:

```sh
python3 tools/check_support_regions.py --output ../support-regions.json
```

The [35-dimensional local-search data](../research/data/d35-local-codes.json)
preserve the 153- and 162-point intermediate signed codes and the rank/size
summary of the 192-point affine construction. The research tests check the two
explicit codes and their common boundary, the regional census, the 45-dimensional
signature domain and the neighbourhood-difference correspondence:

```sh
python3 -m unittest discover -s tests -p test_research.py -v
```

## Paper and reports

Install a TeX distribution with XeLaTeX, BibTeX, latexmk, the Noto CJK fonts,
and the packages named in each report's `latex/preamble.tex`.

Build the mathematical paper with:

```sh
make paper
```

This writes [paper/main.pdf](../paper/main.pdf), keeping intermediate files in
`build/paper/`. Its source project is independent of the reports; its finite
inputs and verifiers are in `constructions/`.

To compile from the paper source directory itself, use
`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`.
`make source-paper` creates `dist/kissing-number-paper-source.zip` with
`main.tex` at the root and only the sources used by the manuscript.
The [finite-data supplement](../reports/en_full/certificates.zip) is distributed
separately; its README gives the verification commands.

For the livestream reports:

```sh
make reports
make reports-en
make reports-zh
make source-en
make source-zh
```

The published livestream report remains in `reports/en/` and `reports/zh/`.
`make reports` checks those files against their published identities; it does
not regenerate the PDFs or attachments. The source commands package the
unchanged files as standalone LaTeX projects.

The complete research report is a separate project in `reports/en_full/`
and `reports/zh_full/`. Build and package it with:

```sh
make reports-full
make source-full-en
make source-full-zh
```

Its output paths and archive names are separate from the livestream report.

The source archives under `dist/` compile independently with
`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`.

Each PDF embeds its own report's `certificates.zip`. Extract it from the PDF attachment panel
or with `pdfdetach -saveall main.pdf`, then follow its README to run the same
finite-input checks. The English and Chinese attachments are byte-identical.
The extraction command is provided by Poppler; some browser PDF viewers
do not display attachments.

## File integrity and tests

```sh
make integrity
make test
```

The integrity check covers the distributed files; tests check the result tables,
document links and input-handling rules. The mathematical replay is the separate
`make verify` command.

After rebuilding reports or making intentional changes, use
`python3 tools/make_manifest.py` to record the updated distributed files.
