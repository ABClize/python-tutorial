"""Run every numbered interview example and report a compact summary."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRACTICE_DIR = ROOT / "python_interview_practice"


def discover_examples() -> list[Path]:
    """Return numbered examples in their intended learning order."""
    return sorted(PRACTICE_DIR.glob("[0-9][0-9]_*.py"))


def run_example(path: Path) -> tuple[bool, str]:
    """Run one example in a separate process so examples cannot share state."""
    completed = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        return True, ""
    detail = completed.stderr.strip() or completed.stdout.strip()
    return False, detail


def main() -> int:
    examples = discover_examples()
    failures: list[tuple[Path, str]] = []

    print(f"发现 {len(examples)} 个面试示例：")
    for path in examples:
        success, detail = run_example(path)
        mark = "✓" if success else "✗"
        print(f"  {mark} {path.name}")
        if not success:
            failures.append((path, detail))

    if failures:
        print("\n失败详情：")
        for path, detail in failures:
            print(f"\n[{path.name}]\n{detail}")
        return 1

    print("\n全部示例运行成功。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
