#!/usr/bin/env python3
"""Run fixed-input mathematical checks in a separate writable copy."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from package_files import files, sha256, write_json

ROOT = Path(__file__).resolve().parents[1]


def receipt_passes(receipt, expected):
    for dotted, value in expected.items():
        current = receipt
        for key in dotted.split("."):
            if not isinstance(current, dict) or key not in current:
                return False
            current = current[key]
        if type(current) is not type(value) or current != value:
            return False
    return True


def prepare_output(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output == root or output.is_relative_to(root):
        raise ValueError("Choose a new output directory outside the source package")
    output.mkdir(parents=True, exist_ok=False)
    return output


def missing_dependencies(requirements):
    missing = []
    for name in sorted(requirements):
        if name in ("c++", "g++"):
            if not shutil.which(os.environ.get("CXX", "c++")):
                missing.append("C++ compiler (CXX or c++)")
        elif importlib.util.find_spec(name) is None:
            missing.append(name)
    return missing


def input_digest(source):
    """Identify the copied verification code and mathematical input files."""
    entries = []
    for path in files(source):
        relative = path.relative_to(source)
        if (relative.parts[:2] == ("constructions", "catalog")
                or path.suffix == ".md"
                or path.name in ("source-manifest.json", "verification.json")):
            continue
        entries.append({"path": relative.as_posix(), "sha256": sha256(path)})
    entries.sort(key=lambda entry: entry["path"])
    records = "".join(entry["path"] + " " + entry["sha256"] + "\n" for entry in entries)
    return {
        "sha256": hashlib.sha256(records.encode("utf-8")).hexdigest(),
        "format": "SHA-256 of UTF-8 records sorted by path, each path + space + file SHA-256 + newline",
        "files": entries,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--suite", default="all", help="a suite name, one job ID, or all")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    plan_bytes = (root / "tools/replay_plan.json").read_bytes()
    plan = json.loads(plan_bytes)
    if plan.get("schema_version") != 1:
        parser.error("Unsupported replay-plan schema")
    if args.list:
        for job in plan["jobs"]:
            print(f'{job["id"]:28} [{job["suite"]}] {job["description"]}')
        return
    jobs = [job for job in plan["jobs"]
            if args.suite in ("all", job["suite"], job["id"])]
    if not jobs:
        parser.error("No registered fixed-input checks match the requested suite")
    if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE"):
        parser.error("Run without optimization; some verifiers use assertions")
    if args.output is None:
        parser.error("--output is required")
    needed = set().union(*(set(job["requirements"]) for job in jobs))
    missing = missing_dependencies(needed)
    if missing:
        parser.error("Missing dependencies: " + ", ".join(missing))
    if any(path.is_symlink() for path in files(root)):
        parser.error("The frozen package must not contain symbolic links")
    try:
        output = prepare_output(root, args.output)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    source = output / "inputs"
    source.mkdir()
    driver_files = {name: Path(__file__).with_name(name).read_bytes()
                    for name in ("reproduce.py", "package_files.py")}
    for name in ("constructions", "tools"):
        if (root / name).is_dir():
            shutil.copytree(root / name, source / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))
    # --root may differ from this driver's checkout: record the driver actually used.
    for name, content in driver_files.items():
        (source / "tools" / name).write_bytes(content)
    (source / "tools/replay_plan.json").write_bytes(plan_bytes)
    logs = output / "logs"
    logs.mkdir()
    tokens = {"python": sys.executable, "tools": str(source / "tools"),
              "source": str(source), "output": str(output)}
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                       DOT_SAGE=str(output / ".sage"))
    versions = {"python": platform.python_version()}
    for name in sorted(needed - {"sage", "c++", "g++"}):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    if "sage" in needed:
        from sage.env import SAGE_VERSION
        versions["sagemath"] = SAGE_VERSION
    report = {"started_at_utc": datetime.now(timezone.utc).isoformat(),
              "suite": args.suite, "versions": versions,
              "scope": "exact verification of the supplied finite constructions",
              "input_digest": input_digest(source), "passed": False, "checks": []}
    try:
        for job in jobs:
            command = [token.format_map(tokens) for token in job["command"]]
            start = time.monotonic()
            log = logs / (job["id"] + ".log")
            print(f'Running {job["id"]}', flush=True)
            with log.open("w") as stream:
                result = subprocess.run(command, cwd=source, env=environment, stdout=stream,
                                        stderr=subprocess.STDOUT, timeout=job["timeout"])
            receipt_file = output / job["receipt"]
            passed = result.returncode == 0 and receipt_file.is_file()
            if passed:
                passed = receipt_passes(json.loads(receipt_file.read_text()), job["checks"])
            entry = {"id": job["id"], "exit_code": result.returncode,
                     "passed": passed, "seconds": round(time.monotonic()-start, 3)}
            report["checks"].append(entry)
            if not passed:
                raise RuntimeError("Verification failed: " + job["id"] + "; inspect its log")
        report["inputs_unchanged"] = input_digest(source)["sha256"] == report["input_digest"]["sha256"]
        if not report["inputs_unchanged"]:
            raise RuntimeError("A verifier modified the copied inputs; inspect the output directory")
        report["passed"] = True
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        report["failure"] = type(exc).__name__
        print(str(exc), file=sys.stderr)
    finally:
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(output / "reproduction.json", report)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
