# csOrchestrator

## 📦 Project Overview

csOrchestrator is a centralized project manager

## 📁 Repository Structure

```
csOrchestrator/
├── src/csorchestrator/              # installable package (src-layout)
│   ├── core/                        # generic building blocks (Report, Expected, etc.)
│   ├── orchestrator/                # orchestrator engine, phases, steps, visitor base
│   ├── visitors/                    # concrete visitor implementations (validator, executor)
│   ├── step/                        # step type definitions (git clone, cmake, echo, etc.)
│   ├── context/                     # execution context (local, GitHub Actions)
│   ├── utils/                       # helpers (file-system, git operations)
│   ├── cli.py                       # command-line entry point
│   └── py.typed                     # PEP 561 type-annotation marker
├── tests/                           # pytest suites mirroring src/ (excluded from linting)
├── .github/workflows/ci.yml         # GitHub Actions CI pipeline
├── conftest.py                      # pytest custom markers (slow, git) and CLI flags
├── pyproject.toml                   # project metadata, deps, and tool config (ruff, mypy, pytest)
├── constraints-minimum.txt          # pinned minimum dependency versions for CI
├── .pre-commit-config.yaml          # pre-commit hooks (ruff, mypy, unstaged-changes check)
├── .gitignore                       # git ignore patterns
├── .gitattributes                   # line-ending normalization
├── LICENSE                          # MIT license
└── README.md                        # this file
```

---

## 🛠 Development Setup

### ⚡ Quick Start

#### Fastest Way (Using Setup Scripts)

**Linux/macOS:**
```bash
./setup.sh              # Run ONCE to set up venv, deps, and pre-commit hooks
./open-code.sh         # Open VS Code with venv activated
```

**Windows (PowerShell):**
```powershell
.\\setup.ps1           # Run ONCE to set up venv, deps, and pre-commit hooks
.\\open-code.ps1      # Open VS Code with venv activated
```

- **`setup.sh` / `setup.ps1`** _(one-time only)_ – Automates: create venv, install deps, install pre-commit hooks
- **`open-code.sh` / `open-code.ps1`** _(convenient shortcut)_ – Activates the virtual environment and opens VS Code (useful for subsequent sessions)

#### Manual Step-by-Step

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

---


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

---

### Install Development Dependencies

All development tools are listed as optional dependencies in `pyproject.toml`:

```bash
pip install -e .[dev]
```

This installs:
- `pytest` - Testing framework
- `mypy` - Static type checking
- `ruff` - Linting and formatting
- `pre-commit` - Git hook automation


---

### Install Pre-Commit Hooks

``` bash
pre-commit install
```

Pre-commit hooks run automatically before each commit.

---

### Bump precommit hooks to last version

``` bash
pre-commit autoupdate
```

will update the `rev` version in `.pre-commit-config.yaml`

or

``` bash
pre-commit autoupdate --repo https://github.com/pre-commit/mirrors-mypy
```

to bump version of a specific repo only


---

### 🔍 Run Pre-Commit Manually

``` bash
pre-commit run --all-files
```

---

## 🔧 VS Code Helpers

This project includes VS Code configurations for streamlined development:

### Launch Configurations (Debugging)

The `.vscode/launch.json` file contains pre-configured debug configurations:

- **▶ Debug all tests** – Runs all pytest tests with debugger enabled (`-s` flag for output)
- **📁 Module-level test suites** – Quick debug access to test directories:
  - `tests/csorchestrator/context`
  - `tests/csorchestrator/core`
  - `tests/csorchestrator/orchestrator`
  - `tests/csorchestrator/step`
  - `tests/csorchestrator/utils/filesystem`
  - `tests/csorchestrator/utils/git`
- **🧪 Individual test cases** – Auto-generated configurations for specific test functions

**How to use:**
1. Open the Debug view (Ctrl+Shift+D / Cmd+Shift+D)
2. Select a configuration from the dropdown
3. Press F5 or click "Run and Debug"

_Note: `launch.json` is **fully auto-generated** by a tool in `tools/`. It's automatically kept in sync and validated by a pre-commit hook, so you should never edit it manually._

### Build & Development Tasks

The `.vscode/tasks.json` file provides convenient task runners:

- **Create venv** – Creates a Python virtual environment at `.venv`
- **Install deps** – Installs the package in editable mode with dev dependencies
- **Pre-commit install** – Sets up git hooks for automatic checks
- **Pre-commit run (all files)** – Manually trigger all pre-commit checks
- **Setup Project** – Runs all tasks above in sequence (recommended for initial setup)

**How to use:**
1. Open the Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type "Tasks: Run Task"
3. Select the task you want to run

Alternatively, use the terminal: `./setup.sh` or `./setup.ps1`.

---

## ✅ Toolchain

-   Formatting & Linting → Ruff
-   Pre-commit enforcement → pre-commit
-   CI → GitHub Actions

---

## Precommits

Before every commit, the project runs automated checks to guarantee consistency, formatting, and repository integrity.

The following checks are enforced:

- 🎨 **Code Formatting** – Formats Python code using `ruff-format`.
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
├── core/                        # generic types: Report, Expected[T,E], OptionalResultWithReport[T]
├── orchestrator/                # engine: Orchestrator, Phase, StepBase, OrchestratorExecutor, visitor base
├── visitors/                    # concrete visitors: validator, local executor
├── step/                        # step definitions: get_repository, cmake, custom_command, echo, etc.
├── context/                     # execution contexts: local filesystem, GitHub Actions
├── utils/
│   ├── file_system/             # path validation, directory creation
│   └── git/                     # clone/checkout, repo sync helpers
├── cli.py                       # CLI entry point (registered as console_script)
└── py.typed                     # PEP 561 marker for downstream type checkers
```

**Why src-layout?** It prevents import shadowing (ensures `import csorchestrator` always loads the installed package, not a local directory) and makes the structure explicit.

---

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

---

### Running the tests

The `tests/` directory contains pytest suites for each module (excluded from linting/type-checking).

```bash
# After installation (`pip install -e .`):
pytest
```

If you want to check code coverage, use one of

```bash
    # report to htmlcov/ folder
    pytest --cov=csorchestrator --cov-branch --cov-report=html

    # report to terminal
    pytest --cov=csorchestrator --cov-branch --cov-report=term

    # report to terminal with details on uncovered lines/blocks
    pytest --cov=csorchestrator --cov-branch --cov-report=term-missing
```

you can also combine multiple `--cov-report=` in the same command line

---

### Continuous Integration

Continuous integration runs

- repo checkout
- `pre-commit`
- pytest with coverage

on a matrix of different OS and python versions

check the `.github\workflows\ci.yml` file for details

---

### Dependencies

- **Runtime:** `GitPython`
- **Development:** `pytest`, `mypy`, `ruff`, `pre-commit`

Install all with: `pip install -e .[dev]`
