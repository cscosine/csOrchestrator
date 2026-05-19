#!/usr/bin/env python3
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath

LAUNCH_PATH = Path(".vscode/launch.json")


def normalize_nodeid(nodeid: str) -> tuple[str, str]:
    """Split a pytest node id into (posix_file_stem, test_part)."""
    file_part, test_part = nodeid.split("::", 1)
    file_part = file_part.replace("\\", "/")
    file_clean = str(PurePosixPath(file_part).with_suffix(""))
    return file_clean, test_part


def collect_tests() -> list[tuple[str, str, str]] | None:
    result = subprocess.run(
        ["pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"pytest collection failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        return None

    lines = result.stdout.splitlines()
    tests = {line.strip() for line in lines if "::" in line and not line.startswith("=")}

    normalized = []
    for t in tests:
        file_clean, test_part = normalize_nodeid(t)
        normalized.append((file_clean, test_part, t))

    normalized.sort(key=lambda x: (x[0], x[1]))
    return normalized


def build_configs(normalized: list[tuple[str, str, str]]) -> list[dict[str, object]]:
    by_folder: dict[str, list[str]] = defaultdict(list)
    for file_clean, _, raw in normalized:
        folder = str(PurePosixPath(file_clean).parent)
        by_folder[folder].append(raw)

    configs: list[dict[str, object]] = []

    configs.append(
        {
            "name": "▶ Debug all tests",
            "type": "debugpy",
            "request": "launch",
            "module": "pytest",
            "args": ["-s"],
            "justMyCode": False,
        }
    )

    for folder in sorted(by_folder.keys()):
        configs.append(
            {
                "name": f"📁 {folder} tests",
                "type": "debugpy",
                "request": "launch",
                "module": "pytest",
                "args": [folder],
                "justMyCode": False,
            }
        )

    for file_clean, test_part, raw in normalized:
        configs.append(
            {
                "name": f"🧪 {file_clean} → {test_part}",
                "type": "debugpy",
                "request": "launch",
                "module": "pytest",
                "args": [raw],
                "justMyCode": False,
            }
        )

    return configs


def main() -> int:
    normalized = collect_tests()
    if normalized is None:
        return 1

    configs = build_configs(normalized)

    new_content = json.dumps({"version": "0.2.0", "configurations": configs}, indent=2)
    # ensure new line at the end
    new_content += "\n"

    LAUNCH_PATH.parent.mkdir(exist_ok=True)

    if LAUNCH_PATH.exists():
        old_content = LAUNCH_PATH.read_text(encoding="utf-8")
        if old_content == new_content:
            print(f"launch.json is up to date ({len(configs)} configurations)")
            return 0

    LAUNCH_PATH.write_text(new_content, encoding="utf-8")
    print(f"launch.json was out of date — updated with {len(configs)} configurations.")
    print("Please stage .vscode/launch.json and re-commit.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
