# Reproducing the results

The reports give the geometric proofs; the verification programs check their
finite inputs. All construction data are included.

## Mathematical verification

Use Python 3.10 or later with NumPy and SymPy. The QR-neighbour and
45-dimensional moment checks also require SageMath. The independent code
checker requires a C++17 compiler, selected by `CXX` or `c++`.

Activate a Python environment providing these libraries:

```sh
python3 -c 'import numpy, sympy; from sage.all import QQ'
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
| Layered codes | Generator ranks, code distances, support intersections and exact exchanges |
| Signed replacements | Regeneration of Hadamard images and all boundary products |
| Equatorial completion | Leech shell, tail data, rational rotation and added lines |
| Lattice sections | Ambient lattice, complete signature domains, moment identities and witnesses |

The exact job list is in [replay_plan.json](../tools/replay_plan.json).
[Recorded verification](../evidence/verification.json) accompanies the data.
[Sources and permissions](../constructions/third-party.md) identify the inputs
used from earlier work.

## Reports

Install a TeX distribution with XeLaTeX, BibTeX, latexmk, the Noto CJK fonts,
and the packages named in each report's `latex/preamble.tex`.

```sh
make reports
make reports-en
make reports-zh
make source-en
make source-zh
```

Each language uses one master file, `reports/en/main.tex` or
`reports/zh/main.tex`, with its sections, bibliography and figures alongside it.
The source archives under `dist/` compile independently with
`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`.

Each PDF embeds `certificates.zip`. Extract it from the PDF attachment panel
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
