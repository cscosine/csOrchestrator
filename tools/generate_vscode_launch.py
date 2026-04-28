import json
import re
import subprocess
from pathlib import Path

# Run pytest collection
result = subprocess.run(["pytest", "--collect-only", "-q"], capture_output=True, text=True)

lines = result.stdout.splitlines()

# Extract test nodeids (pytest format: file.py::test_name)
tests = []
pattern = re.compile(r".*::.*")

for line in lines:
    line = line.strip()
    if "::" in line and not line.startswith("="):
        tests.append(line)

# Build VS Code configs
configs = []

# global config
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

# per-test configs
for t in sorted(set(tests)):
    safe_name = t.replace("::", " → ")
    configs.append(
        {
            "name": f"🧪 {safe_name}",
            "type": "debugpy",
            "request": "launch",
            "module": "pytest",
            "args": [t],
            "justMyCode": False,
        }
    )

launch = {"version": "0.2.0", "configurations": configs}

Path(".vscode").mkdir(exist_ok=True)

with open(".vscode/launch.json", "w", encoding="utf-8") as f:
    json.dump(launch, f, indent=2)

print(f"Generated {len(configs)} debug configurations")
