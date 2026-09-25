#!/usr/bin/env python3
"""Create a self-contained LaTeX source archive for either report."""
import argparse
from pathlib import Path
import zipfile
from build_reports import build

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {".tex", ".bib", ".png", ".pdf"}


def package(root, language):
    root = Path(root)
    build(root, language)
    source = root / "reports" / language
    output = root / "dist" / ("kissing-number-report-" + language + ".zip")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise ValueError("Report sources must be regular files")
            if path.is_file() and (path.suffix in SUFFIXES or path.name == "certificates.zip"):
                archive.write(path, path.relative_to(source).as_posix())
        for name in ("LICENSE", "CITATION.cff"):
            archive.write(root / name, name)
        archive.writestr("README.md", "# Kissing number research report\n\n"
                        "Compile with XeLaTeX and BibTeX:\n\n"
                        "`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`\n\n"
                        "The Chinese edition requires the Noto CJK fonts.\n\n"
                        "`certificates.zip` contains the construction data and verification programs.\n"
                        "It is also embedded in the PDF and described in its finite-data appendix.\n")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--language", choices=("en", "zh"), default="en")
    args = parser.parse_args()
    print(package(args.root, args.language))


if __name__ == "__main__":
    main()
