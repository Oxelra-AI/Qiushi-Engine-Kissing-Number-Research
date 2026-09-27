# Research reports

Qiushi Engine's autonomous investigation of the kissing-number problem
connects coding theory, lattice geometry and combinatorics to produce new
constructions. The reports develop the mathematical ideas behind these
discoveries, from the freedom left by distance constraints to methods for
building and counting larger configurations.

Each report has matching English and Chinese editions, with complete LaTeX
sources, mathematical statements, data and bibliography.

## Apsara Conference livestream report

The published report covers dimensions 32–39, 43 and 45. Its PDFs, source
files and embedded certificates remain at their original locations.

| Language | Read | Edit |
|---|---|---|
| English | [Report](en/main.pdf) | [LaTeX source](en/main.tex) |
| 中文 | [报告](zh/main.pdf) | [LaTeX 源码](zh/main.tex) |

`make reports` checks the published files without rebuilding or replacing them.
`make source-en` and `make source-zh` package these unchanged reports and sources.

## Complete research report

The complete study has its own report projects. It brings together the
geometric arguments, finite constructions and research accounts across all
dimensions in the [result catalogue](../research/results.md).
Its nineteen dimensions are 25, 27, 32–39, 43, 45 and 49–55.

| Language | Read | Edit |
|---|---|---|
| English | [Complete report](en_full/main.pdf) | [LaTeX source](en_full/main.tex) |
| 中文 | [完整研究报告](zh_full/main.pdf) | [LaTeX 源码](zh_full/main.tex) |

The four report directories are siblings: `en/` and `zh/` hold the
livestream edition; `en_full/` and `zh_full/` hold the complete study.
The paper [*Large-Scale Autonomous Discovery of Kissing Number Constructions*](../paper/main.pdf) has its own
[LaTeX source project](../paper/main.tex), compiled with `make paper`.

`make reports-full` builds these two reports. `make source-full-en` and
`make source-full-zh` create their separately named LaTeX archives.

All source archives are written under `dist/` and compile with XeLaTeX and
BibTeX. Each PDF embeds the `certificates.zip` for its own report. The two
language editions of a report use the same attachment. Save it from the PDF
attachment panel, or use `pdfdetach -saveall main.pdf`; its README gives
the reproduction commands. The source archives include it as well.
See the [build instructions](../reproducibility/README.md).
