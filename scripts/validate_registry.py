#!/usr/bin/env python3
"""Validate the published NixScript registry index and package files."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.txt"
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
VERSION_PATTERN = re.compile(r"^(0|[1-9][0-9]*)[.](0|[1-9][0-9]*)[.](0|[1-9][0-9]*)$")
MAIN_PATTERN = re.compile(r"(?m)^ *nix +main *[(]")


def main() -> int:
    if not INDEX.is_file():
        print("ERROR: missing registry index.txt", file=sys.stderr)
        return 1

    packages: dict[str, str] = {}
    errors: list[str] = []

    try:
        lines = INDEX.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        print("ERROR: index.txt must be UTF-8 text", file=sys.stderr)
        return 1

    for number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        fields = line.split()
        if len(fields) != 2:
            errors.append(f"index.txt:{number}: expected 'name MAJOR.MINOR.PATCH'")
            continue

        name, version = fields
        if not NAME_PATTERN.fullmatch(name):
            errors.append(f"index.txt:{number}: invalid package name {name!r}")
            continue
        if not VERSION_PATTERN.fullmatch(version):
            errors.append(f"index.txt:{number}: invalid semantic version {version!r}")
            continue
        if name in packages:
            errors.append(f"index.txt:{number}: duplicate package entry {name!r}")
            continue

        packages[name] = version
        package_path = ROOT / "libraries" / name / version / f"{name}.ns"
        if not package_path.is_file():
            errors.append(f"index.txt:{number}: missing package file {package_path.relative_to(ROOT)}")
            continue

        try:
            source = package_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{package_path.relative_to(ROOT)}: package must be UTF-8 text")
            continue

        if not source.strip():
            errors.append(f"{package_path.relative_to(ROOT)}: package file is empty")
        if MAIN_PATTERN.search(source):
            errors.append(
                f"{package_path.relative_to(ROOT)}: libraries must not define 'nix main()'"
            )

    if not packages:
        errors.append("index.txt contains no package entries")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(packages)} official package(s).")
    for name, version in sorted(packages.items()):
        print(f"  {name} {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
