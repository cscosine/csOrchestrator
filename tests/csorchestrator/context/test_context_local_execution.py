from pathlib import Path
from unittest.mock import patch

import pytest

from csorchestrator.foundation.core.expected import Expected
from csorchestrator.frontend.local_execution.validate_and_execute import create_os_and_path


def test_create_context_empty_path_invalid() -> None:
    cr = create_os_and_path("")
    assert not cr.has_result()
    assert cr.report.has_errors()


def test_create_context_invalid_detect_context_os_architecture() -> None:
    with patch(
        "csorchestrator.domain.context.context_os_architecture.detect_context_os_architecture",
        return_value=Expected.make_error("Unsupported OS"),
    ):
        cr = create_os_and_path("")

    assert not cr.has_result()
    assert cr.report.has_errors()


def test_local_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # change local directory to tmp_path
    monkeypatch.chdir(tmp_path)

    cr = create_os_and_path("./")

    assert cr.has_result()
    assert not cr.report.has_errors()
    assert cr.result is not None
    assert cr.result.path == tmp_path.resolve()
