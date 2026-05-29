import textwrap
from pathlib import Path

import pytest

from csorchestrator.cli.cli import main as csorchestrator_main


def test_run_command_loads_project_script(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script_path = tmp_path / "project.py"
    script_path.write_text(
        textwrap.dedent(
            """
            from typing import TypeAlias
            from csorchestrator.core.report import Report
            from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
            from csorchestrator.orchestrator.orchestrator import Orchestrator, OptionalOrchestratorWithReport

            def create_orchestrator() -> OptionalOrchestratorWithReport:
                return OptionalOrchestratorWithReport.createResultAndReport(Orchestrator("myName"), Report())
            """
        )
    )

    executed = {"called": False}

    def fake_validate_and_execute_orchestrator(orchestrator, target_folder_path, reporter):
        assert Path(target_folder_path) == script_path.parent
        executed["called"] = True
        return None

    from csorchestrator.cli import cli as mod

    monkeypatch.setattr(mod, "validate_and_execute_orchestrator", fake_validate_and_execute_orchestrator)

    result = csorchestrator_main(["run", str(script_path)])

    assert result == 0
    assert executed["called"]


def test_run_command_missing_create_orchestrator(tmp_path: Path) -> None:
    script_path = tmp_path / "project.py"
    script_path.write_text("a = 1\n")

    result = csorchestrator_main(["run", str(script_path)])
    assert result == 1
