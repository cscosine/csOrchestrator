import json
import subprocess
from collections import defaultdict
from pathlib import Path, PurePosixPath


# ----------------------------
# Normalize EVERYTHING to POSIX
# ----------------------------
def normalize_nodeid(nodeid: str) -> tuple[str, str]:
    file_part, test_part = nodeid.split("::", 1)

    # force POSIX separators FIRST (critical)
    file_part = file_part.replace("\\", "/")

    # convert to POSIX path object (never OS-dependent Path here)
    file_clean = str(PurePosixPath(file_part).with_suffix(""))

    return file_clean, test_part


# ----------------------------
# Run pytest collection
# ----------------------------
result = subprocess.run(["pytest", "--collect-only", "-q"], capture_output=True, text=True)

lines = result.stdout.splitlines()

tests = {line.strip() for line in lines if "::" in line and not line.startswith("=")}

# ----------------------------
# Normalize tests
# ----------------------------
normalized = []

for t in tests:
    file_clean, test_part = normalize_nodeid(t)
    normalized.append((file_clean, test_part, t))

# stable cross-platform ordering
normalized.sort(key=lambda x: (x[0], x[1]))

# ----------------------------
# Group by folder (POSIX ONLY)
# ----------------------------
by_folder = defaultdict(list)

for file_clean, _, raw in normalized:
    folder = str(PurePosixPath(file_clean).parent)
    by_folder[folder].append(raw)

# ----------------------------
# Build configs
# ----------------------------
configs = []

# 1. global config
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

# ----------------------------
# 2. per-folder configs FIRST
# ----------------------------
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

# ----------------------------
# 3. per-test configs AFTER
# ----------------------------
for file_clean, test_part, raw in normalized:
    # display MUST stay POSIX (no Path() anywhere here)
    display_file = file_clean

    configs.append(
        {
            "name": f"🧪 {display_file} → {test_part}",
            "type": "debugpy",
            "request": "launch",
            "module": "pytest",
            "args": [raw],
            "justMyCode": False,
        }
    )

# ----------------------------
# Write launch.json
# ----------------------------
Path(".vscode").mkdir(exist_ok=True)

with open(".vscode/launch.json", "w", encoding="utf-8") as f:
    json.dump({"version": "0.2.0", "configurations": configs}, f, indent=2)

print(f"Generated {len(configs)} debug configurations")
