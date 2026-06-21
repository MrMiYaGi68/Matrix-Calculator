# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}
DEFAULT_EXCLUDED_SUFFIXES = {
    ".gz",
    ".pyc",
    ".pyo",
    ".whl",
    ".zip",
}


def should_include(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if any(part in DEFAULT_EXCLUDED_DIRS for part in relative.parts):
        return False
    if any(part.endswith(".egg-info") for part in relative.parts):
        return False
    if path.suffix in DEFAULT_EXCLUDED_SUFFIXES:
        return False
    return True


def build_release_zip(root: Path, output: Path) -> None:
    root = root.resolve()
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if path == output or not path.is_file() or not should_include(path, root):
                continue
            archive.write(path, Path(root.name) / path.relative_to(root))
    validate_release_zip(output)


def validate_release_zip(path: Path) -> None:
    with ZipFile(path) as archive:
        forbidden = [
            name
            for name in archive.namelist()
            if "__pycache__/" in name or name.endswith((".pyc", ".pyo"))
        ]
    if forbidden:
        preview = "\n".join(forbidden[:20])
        raise SystemExit(f"Release ZIP contains bytecode artifacts:\n{preview}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a clean Matrix Calculator release ZIP.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root to package.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "meine-app-clean.zip",
        help="Output ZIP path.",
    )
    args = parser.parse_args()
    build_release_zip(args.root, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
