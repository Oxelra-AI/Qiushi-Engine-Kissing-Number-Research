#!/usr/bin/env python3
"""Build the native LaTeX reports without leaving auxiliary files in their sources."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from supplement import write as write_supplement
from package_files import approved_paths, contained_file
from report_editions import prefix, verify_frozen

ROOT = Path(__file__).resolve().parents[1]


def report_sources(root, language, edition='livestream'):
    if language not in ("en", "zh"):
        raise ValueError("Expected an English or Chinese report source")
    directory = prefix(language, edition) + "/"
    return tuple(name for name in approved_paths(root)
                 if name.startswith(directory) and Path(name).suffix in {".tex", ".bib", ".png"})


def build(root, language, keep_log=True, edition='livestream'):
    directory = prefix(language, edition)
    source = Path(root) / directory
    if language not in ("en", "zh") or not (source / "main.tex").is_file():
        raise ValueError("Expected an English or Chinese report source")
    if edition == 'livestream' and verify_frozen(root):
        return {'language': language, 'edition': edition,
                'pdf': directory + '/main.pdf', 'preserved': True}
    supplement = write_supplement(root, language, edition=edition)
    with tempfile.TemporaryDirectory(prefix="kissing-report-") as temporary:
        work = Path(temporary) / language
        for name in report_sources(root, language, edition):
            target = work / Path(name).relative_to(directory)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(contained_file(root, name), target)
        shutil.copy2(supplement, work / supplement.name)
        result = subprocess.run(
            ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            cwd=work, capture_output=True, text=True, timeout=240)
        if result.returncode:
            raise RuntimeError(result.stdout[-6000:] + result.stderr[-1000:])
        log = (work / "main.log").read_text(errors="replace")
        if keep_log:
            logs = Path(root) / "build/reports"
            logs.mkdir(parents=True, exist_ok=True)
            (logs / (edition + '-' + language + ".log")).write_text(log)
        for problem in ("There were undefined references", "There were undefined citations",
                        "Citation `", "LaTeX Warning: Reference `"):
            if problem in log:
                raise RuntimeError("Unresolved reference in " + language + " report")
        shutil.copy2(work / "main.pdf", contained_file(root, directory + "/main.pdf"))
        return {"language": language, "edition": edition, "pdf": directory + "/main.pdf",
                "overfull_boxes": log.count("Overfull")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--language", choices=("en", "zh", "all"), default="all")
    parser.add_argument("--edition", choices=('livestream', 'complete'), default='livestream')
    args = parser.parse_args()
    for language in (("en", "zh") if args.language == "all" else (args.language,)):
        print(build(args.root, language, edition=args.edition))


if __name__ == "__main__":
    main()
