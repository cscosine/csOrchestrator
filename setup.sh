#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip
pip install -e ".[dev]"

pre-commit install

echo "Setup complete."
echo ""
echo "Next: "
echo "  source .venv/bin/activate"
echo "  code ."
echo ""
echo "Or: "
echo "  ./open-code.sh"
echo ""
echo "Or: "
echo "  source ./open-code.sh"
