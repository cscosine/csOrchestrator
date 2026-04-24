# execution context
import os
import tempfile
from pathlib import Path
from typing import TypeAlias

from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.core.report import Report

ContextLocalExecutionWithReport: TypeAlias = OptionalResultWithReport[Path]


def ensure_directory_exists_or_create_and_is_usable(path: str) -> ContextLocalExecutionWithReport:
    if not path.strip():
        return ContextLocalExecutionWithReport.createReport(
            Report().append_error("create_local_context need a non empty base path string")
        )

    try:
        # Expand ~ and environment variables, then resolve
        p = Path(os.path.expandvars(os.path.expanduser(path))).resolve()
    except Exception as e:
        return ContextLocalExecutionWithReport.createReport(Report().append_error(f"Invalid path '{path}': {e}"))

    try:
        # Create directory if it does not exist
        p.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return ContextLocalExecutionWithReport.createReport(
            Report().append_error(f"Failed to create directory '{p}': {e}")
        )

    # Ensure it's actually a directory
    if not p.is_dir():
        return ContextLocalExecutionWithReport.createReport(
            Report().append_error(f"Path exists but is not a directory: '{p}'")
        )

    # Check readability & writability by attempting real operations
    try:
        # Create a temp file inside the directory
        with tempfile.NamedTemporaryFile(dir=p, delete=True) as tmp:
            tmp.write(b"test")
            tmp.flush()

        # Try creating a subdirectory
        test_subdir = p / "__test_subdir__"
        test_subdir.mkdir(exist_ok=True)
        test_subdir.rmdir()

    except Exception as e:
        return ContextLocalExecutionWithReport.createReport(
            Report().append_error(f"Directory '{p}' is not writable or accessible: {e}")
        )

    return ContextLocalExecutionWithReport.createResultAndReport(p, Report())
