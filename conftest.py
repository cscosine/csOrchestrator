"""Pytest configuration for src-layout package.

This conftest.py adds src/ to sys.path so that tests can import
toc_generator even with editable installs.
"""

import sys
from pathlib import Path

# Add src/ to path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
