# Research reports

The English and Chinese reports share the same structure, mathematical statements,
data and bibliography. Each language is a complete LaTeX project.

| Language | Read | Edit |
|---|---|---|
| English | [Report](en/main.pdf) | [LaTeX source](en/main.tex) |
| 中文 | [报告](zh/main.pdf) | [LaTeX 源码](zh/main.tex) |

`make reports` builds both PDFs with XeLaTeX and BibTeX.
`make source-en` and `make source-zh` produce self-contained source archives
under `dist/`. Each archive includes the report PDF, sources, bibliography
and figures. Both PDFs embed the same `certificates.zip`, containing the
complete finite inputs and verification programs. Save it from the PDF
attachment panel, or use `pdfdetach -saveall main.pdf`; its README gives
the exact reproduction commands. The source archives include it as well.
See the [build instructions](../reproducibility/README.md).
