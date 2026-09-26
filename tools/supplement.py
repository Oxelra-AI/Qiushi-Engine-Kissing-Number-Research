#!/usr/bin/env python3
"""Build the finite-data attachment from the report's selected constructions."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

from package_files import approved_paths, contained_file


def contents(root):
    root = Path(root).resolve()
    approved = set(approved_paths(root))
    plan = json.loads((root / "tools/replay_plan.json").read_text())
    selected = {"LICENSE", "RIGHTS.md", "CITATION.cff", "requirements.txt",
                "tools/package_files.py", "tools/reproduce.py",
                "tools/check_package.py", "tools/replay_plan.json"}
    for job in plan["jobs"]:
        for argument in job["command"]:
            if argument.startswith("{tools}/"):
                selected.add("tools/" + argument[len("{tools}/"):])
    selected.update(name for name in approved if name.startswith("constructions/"))
    if not selected <= approved:
        raise ValueError("A supplement input is absent from the package manifest")
    data = {name: contained_file(root, name).read_bytes() for name in sorted(selected)}
    rows = json.loads(data["constructions/catalog/results.json"])["results"]
    for row in rows:
        if not set(row["artifact_ids"]) <= set(data):
            raise ValueError("A defining input is missing from the supplement")
    data["README.md"] = (
        "# Kissing-number constructions\n\n"
        "Finite data and verification programs accompanying the Qiushi Engine reports.\n"
        "Dimensions: " + ", ".join(str(row["dimension"]) for row in rows) + ".\n\n"
        "The defining inputs and counts are listed in `constructions/catalog/results.json`.\n"
        "Each construction directory describes its coordinates and mathematical sources.\n"
        "The proof is in the report containing this attachment.\n\n"
        "## Verification\n\n"
        "Use Python 3.10 or later, NumPy, SymPy, a C++ compiler and SageMath 10.\n"
        "From this directory, check file integrity, then run all mathematical checks:\n\n"
        "```sh\npython3 tools/check_package.py\n"
        "sage -python tools/reproduce.py --suite all --output ../kissing-verification\n```\n\n"
        "The output directory must be new and outside this extracted package.\n"
        "Use `--list` to see the checks, or `--suite NAME` to run one.\n"
        "No network access is required for the verification.\n\n"
        "The two language editions embed the same archive. All coordinates and programs\n"
        "are copied without alteration from the accompanying repository.\n"
        "`LICENSE`, `RIGHTS.md` and `constructions/third-party.md` state the applicable terms.\n"
    ).encode("utf-8")
    entries = [{"path": name, "bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}
               for name, value in sorted(data.items())]
    data["manifest.json"] = (json.dumps({"schema_version": 1, "scope": "file integrity",
                                        "files": entries}, indent=2) + "\n").encode()
    return data


def archive_bytes(root):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(contents(root).items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return stream.getvalue()


def write(root, language):
    if language not in ("en", "zh"):
        raise ValueError("Expected an English or Chinese report source")
    output = contained_file(root, "reports/" + language + "/certificates.zip")
    output.write_bytes(archive_bytes(root))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--language", choices=("en", "zh"), required=True)
    args = parser.parse_args()
    print(write(args.root, args.language))


if __name__ == "__main__":
    main()
