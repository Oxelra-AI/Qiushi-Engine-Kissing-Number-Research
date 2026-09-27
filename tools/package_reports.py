#!/usr/bin/env python3
"""Create a self-contained LaTeX source archive for either report."""
import argparse
from pathlib import Path
import zipfile
from build_reports import build, report_sources
from package_files import contained_file
from report_editions import prefix

ROOT = Path(__file__).resolve().parents[1]


def package(root, language, edition='livestream'):
    root = Path(root)
    build(root, language, edition=edition)
    directory = prefix(language, edition)
    source = root / directory
    label = 'complete-' if edition == 'complete' else ''
    output = root / "dist" / ("kissing-number-report-" + label + language + ".zip")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        names = (*report_sources(root, language, edition),
                 directory + "/main.pdf", directory + "/certificates.zip")
        for name in sorted(names):
            path = contained_file(root, name)
            archive.write(path, path.relative_to(source).as_posix())
        for name in ("LICENSE", "CITATION.cff"):
            archive.write(contained_file(root, name), name)
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
    parser.add_argument("--edition", choices=('livestream', 'complete'), default='livestream')
    args = parser.parse_args()
    print(package(args.root, args.language, args.edition))


if __name__ == "__main__":
    main()
