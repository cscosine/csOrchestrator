from pathlib import Path
from unittest.mock import patch

import pytest

from csorchestrator.core.expected import Expected
from csorchestrator.orchestrator.execution import create_context_local_execution
from csorchestrator.orchestrator.orchestrator import Orchestrator


def test_create_context_empty_path_invalid() -> None:
    cr = create_context_local_execution("", orchestrator=Orchestrator())
    assert not cr.has_result()
    assert cr.report.has_errors()


def test_create_context_invalid_detect_context_os_architecture() -> None:
    with patch(
        "csorchestrator.context.context_os_architecture.detect_context_os_architecture",
        return_value=Expected.make_error("Unsupported OS"),
    ):
        cr = create_context_local_execution("", orchestrator=Orchestrator())

    assert not cr.has_result()
    assert cr.report.has_errors()


def test_local_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # change local directory to tmp_path
    monkeypatch.chdir(tmp_path)

    cr = create_context_local_execution("./", orchestrator=Orchestrator())

    assert cr.has_result()
    assert not cr.report.has_errors()
    assert cr.result is not None
    assert cr.result.base_folder_path == tmp_path.resolve()
