# csOrchestrator

## 📦 Project Overview

csOrchestrator is a centralized project manager

## 📁 Repository Structure

```
csOrchestrator/
├── src/
│   └── csorchestrator/         # the csorchestrator package
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
├── tests/                      # Pytest test suites (excluded from linting)
├── conftest.py                 # Add src/ to python path to execute tests with `pytest`
├── pyproject.toml              # Project metadata & tool configuration
├── .pre-commit-config.yaml     # Pre-commit hooks
├── .github/workflows/ci.yml    # GitHub Actions CI pipeline
├── .gitignore                  # Git ignore patterns
├── .gitattributes              # Git attributes for line endings
└── README.md                   # This file
```

---

## 🛠 Development Setup

### ⚡ Quick Start

```bash
# 1. Clone repository
git clone git@github.com:cscosine/csOrchestrator.git
cd csOrchestrator

# 2. Create virtual environment
python3.XX -m venv .venv # 3.XX >= 3.11
source .venv/bin/activate

# 3. Install package in editable mode with dev dependencies
pip install -e .[dev]

# this
# - Installs the project `.` in editable mode (because of `-e`)
# - Installs the optional dependency group dev normally.

# 4. Run tests directly (package is now importable)
pytest

# 5. Or use pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### 🌍 Detailed Setup

If you prefer step-by-step instructions:

#### Clone Repository

``` bash
git clone git@github.com:cscosine/csOrchestrator.git
```

or

``` bash
git clone https://github.com/cscosine/csOrchestrator.git
```

---

### Create Virtual Environment

``` bash
python -m venv .venv
source .venv/bin/activate
```
_Note_: You may need `python3` instead of `python`.

On Windows:

``` bash
.venv\Scripts\activate
```

or for PowerShell

``` bash
.venv\Scripts\activate.ps1
```

### Install Development Dependencies

All development tools are listed as optional dependencies in `pyproject.toml`:

```bash
pip install -e .[dev]
```

This installs:
- `pytest` - Testing framework
- `mypy` - Static type checking
- `ruff` - Linting and formatting
- `black` - Code formatter
- `pre-commit` - Git hook automation

### Install Pre-Commit Hooks

``` bash
pre-commit install
```

Pre-commit hooks run automatically before each commit.

---

## 🔍 Run Pre-Commit Manually

``` bash
pre-commit run --all-files
```

---

## ✅ Toolchain

-   Formatting → Black
-   Linting → Ruff
-   Static typing → Mypy
-   Pre-commit enforcement → pre-commit
-   CI → GitHub Actions

---

## Precommits

Before every commit, the project runs automated checks to guarantee consistency, formatting, and repository integrity.

The following checks are enforced:

- 🎨 **Code Formatting** – Formats Python code using `black`.
- ⚡ **Linting & Auto-Fix** – Runs `ruff` for style checks, bug detection, and automatic fixes.
- 🧠 **Type Checking** – Validates static types with `mypy`.
- 🔒 **Repository Integrity** – Fails if unstaged changes remain after hooks run (`git diff --quiet`).

If any check fails, the commit is blocked until the issues are resolved.

---

## 🧩 Reusable Module & Testing

The csOrchestrator logic is a installable package in `src/csorchestrator/`. This design allows the library to be used independently-either within this repo or published on PyPI.

### Package structure (src-layout)

```
src/csorchestrator/
├── core/                 # Core lib
```

**Why src-layout?** It prevents import shadowing (ensures `import csorchestrator` always loads the installed package, not a local directory) and makes the structure explicit.

### Using the package

After installation (`pip install -e .`), you can:

1. **Use as a library:**

    ```python
    TODO
    ```

2. **Use the CLI:**

    ```bash
    TODO
    ```

### Running the tests

The `tests/` directory contains pytest suites for each module (excluded from linting/type-checking).

```bash
# After installation (`pip install -e .`):
pytest

# Or without installation, manually add src/:
PYTHONPATH=src pytest
```

**How imports work:** A `conftest.py` file at the project root is automatically loaded by pytest before running tests. It adds `src/` to Python's import path, ensuring tests can find and import `csorchestrator` correctly. This is a standard pytest pattern for src-layout projects and requires no special setup.

All tests pass - the package works independently of the repository structure.

### Dependencies

- **Runtime:** None (stdlib only)
- **Development:** `pytest`, `mypy`, `ruff`, `black`, `pre-commit`

Install all with: `pip install -e .[dev]`
