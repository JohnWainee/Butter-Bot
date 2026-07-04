"""CI lint runner: `python -m butter_bot.style <paths>`.

Prints every violation and exits nonzero when any error-severity
violation exists. Warnings report but do not gate.
"""

import argparse
import sys
from pathlib import Path

from .engine import lint_paths
from .models import Severity


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m butter_bot.style")
    parser.add_argument("paths", nargs="+", type=Path, help="markdown files or directories")
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as errors for the exit code"
    )
    args = parser.parse_args(argv)

    violations = lint_paths(args.paths)
    for v in violations:
        print(f"{v.path}:{v.line}:{v.column} [{v.severity.value}] {v.rule_id}: {v.message}")

    errors = sum(1 for v in violations if v.severity is Severity.ERROR)
    warnings = len(violations) - errors
    print(f"\n{errors} error(s), {warnings} warning(s)")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
