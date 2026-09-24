#!/usr/bin/env python3
"""Audit SVN diffs for shader keyword deletion changes.

The input report is the CSV emitted by ``shader_keyword_audit.py --delete``.
For every reported resource this script checks:

* the SVN status is a normal ``M`` modification;
* there are no property changes, conflicts, missing files, or unversioned files;
* changed lines belong only to ``m_ShaderKeywords`` / ``m_ValidKeywords`` or
  ``keywords`` entries.

This script is intentionally conservative and returns a non-zero exit code when
it cannot prove those invariants.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path


REPORT_LINE_RE = re.compile(r"^(?P<code>M)\s+(?P<path>.+)$")
CHANGED_LINE_RE = re.compile(r"^[+-][^+-]")
INDEX_RE = re.compile(r"^Index: (.+)$")
ALLOWED_CHANGE_RE = re.compile(
    r"^\s*(?:-\s*)?(?:m_ShaderKeywords:|m_ValidKeywords:|keywords:)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit SVN diffs for report files changed by shader keyword deletion."
    )
    parser.add_argument(
        "--report",
        type=Path,
        required=True,
        help="CSV report emitted by shader_keyword_audit.py --delete",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="optional directory for per-batch diff output",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="number of files per svn diff invocation (default: 50)",
    )
    return parser.parse_args()


def read_report(path: Path) -> list[Path]:
    paths: list[Path] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            source = (row.get("source") or "").strip()
            if source:
                paths.append(Path(source))
    return paths


def resolve_svn() -> str:
    command = shutil.which("svn")
    if not command:
        raise RuntimeError("svn executable was not found in PATH")
    return command


def run_command(command: list[str]) -> str:
    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return process.stdout


def audit_statuses(svn: str, paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for index in range(0, len(paths), 200):
        batch = paths[index : index + 200]
        output = run_command([svn, "status", "--depth", "empty", *map(str, batch)])
        status_by_path: dict[str, str] = {}
        for line in output.splitlines():
            match = re.match(r"^(?P<code>\S+)\s+(?P<path>.+)$", line)
            if match:
                status_by_path[match.group("path")] = match.group("code")

        for path in batch:
            code = status_by_path.get(str(path))
            if code is None:
                errors.append(f"missing svn status: {path}")
            elif code != "M":
                errors.append(f"non-M svn status {code}: {path}")
    return errors


def audit_diff_text(text: str, current_file: str, errors: list[str]) -> tuple[int, int]:
    changed = 0
    suspect = 0
    current = current_file
    for line in text.splitlines():
        index_match = INDEX_RE.match(line)
        if index_match:
            current = index_match.group(1)
            continue
        if not CHANGED_LINE_RE.match(line):
            continue
        changed += 1
        body = line[1:].strip()
        if not ALLOWED_CHANGE_RE.match(body):
            suspect += 1
            errors.append(f"non-keyword change: {current}: {line.strip()}")
    return changed, suspect


def main() -> int:
    args = parse_args()
    report = args.report.resolve()
    if not report.is_file():
        print(f"error: report not found: {report}", file=sys.stderr)
        return 2

    paths = read_report(report)
    print(f"Report files : {len(paths)}")
    if not paths:
        print("No files to audit.")
        return 0

    try:
        svn = resolve_svn()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    errors = audit_statuses(svn, paths)
    if errors:
        print("SVN status audit failed:")
        for error in errors[:100]:
            print(f"  {error}")
        return 1

    output_dir = args.output_dir.resolve() if args.output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    total_changed = 0
    total_suspect = 0
    batch_size = max(1, args.batch_size)
    for batch_index, start in enumerate(range(0, len(paths), batch_size)):
        batch = paths[start : start + batch_size]
        text = run_command([svn, "diff", "--depth", "empty", *map(str, batch)])
        if output_dir:
            (output_dir / f"diff_{batch_index:04d}.txt").write_text(
                text, encoding="utf-8"
            )
        changed, suspect = audit_diff_text(text, str(batch[0]), errors)
        total_changed += changed
        total_suspect += suspect
        print(
            f"Batch {batch_index:04d}: files={len(batch)} "
            f"changed={changed} suspect={suspect}"
        )

    print(f"Changed lines : {total_changed}")
    print(f"Suspect lines : {total_suspect}")
    if errors:
        print("Diff audit failed:")
        for error in errors[:200]:
            print(f"  {error}")
        return 1

    print("SVN diff audit passed: only keyword fields changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
