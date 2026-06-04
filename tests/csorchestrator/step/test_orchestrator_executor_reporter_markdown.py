from pathlib import Path

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.execution import validate_and_execute_orchestrator
from csorchestrator.orchestrator.orchestrator import create_orchestrator_factory
from csorchestrator.reporters.orchestrator_executor_reporter_markdown import OrchestratorExecutorReporterMarkdown
from csorchestrator.step.step_echo_message import StepEchoMessage


def test_markdown_reporter_produces_valid_file(tmp_path: Path) -> None:
    report_path = tmp_path / "execution_report.md"
    reporter = OrchestratorExecutorReporterMarkdown(path=report_path)

    # 1. Test Creation Report
    creation_report = Report()
    creation_report.append_info("Orchestrator Initialized")
    creation_report.append_warning("Non-critical config issue")
    reporter.report_orchestrator_creation_report(creation_report)

    # 2. Test Execution Description
    orchestrator = create_orchestrator_factory("myName", "0.0.0", "exec-job")
    phase = orchestrator.create_phase("Build")
    phase.add_step(StepEchoMessage(name="Compile", description="Compiling...", message="Compiling..."))

    validate_and_execute_orchestrator(orchestrator, target_folder_path=str(tmp_path), reporter=reporter)

    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "## Creation Report" in content
    assert "Orchestrator Initialized" in content
    assert "Non-critical config issue" in content
    assert "Phase: Build" in content
    assert "Step: Compile" in content
