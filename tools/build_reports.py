#!/usr/bin/env python3
"""Build the native LaTeX reports without leaving auxiliary files in their sources."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from supplement import write as write_supplement

ROOT = Path(__file__).resolve().parents[1]


def build(root, language, keep_log=True):
    source = Path(root) / "reports" / language
    if language not in ("en", "zh") or not (source / "main.tex").is_file():
        raise ValueError("Expected an English or Chinese report source")
    supplement = write_supplement(root, language)
    with tempfile.TemporaryDirectory(prefix="kissing-report-") as temporary:
        work = Path(temporary) / language
        shutil.copytree(source, work, ignore=shutil.ignore_patterns("*.pdf", "*.zip"))
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
            (logs / (language + ".log")).write_text(log)
        for problem in ("There were undefined references", "There were undefined citations",
                        "Citation `", "LaTeX Warning: Reference `"):
            if problem in log:
                raise RuntimeError("Unresolved reference in " + language + " report")
        shutil.copy2(work / "main.pdf", source / "main.pdf")
        return {"language": language, "pdf": "reports/" + language + "/main.pdf",
                "overfull_boxes": log.count("Overfull")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--language", choices=("en", "zh", "all"), default="all")
    args = parser.parse_args()
    for language in (("en", "zh") if args.language == "all" else (args.language,)):
        print(build(args.root, language))


if __name__ == "__main__":
    main()
