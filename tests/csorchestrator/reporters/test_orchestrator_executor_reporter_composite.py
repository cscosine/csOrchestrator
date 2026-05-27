from dataclasses import dataclass
from pathlib import Path

import pytest

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.orchestrator_executor import execute_orchestrator
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.reporters.orchestrator_executor_reporter_composite import OrchestratorExecutorReporterComposite
from csorchestrator.reporters.orchestrator_executor_reporter_dummy import OrchestratorExecutorReporterDummy
from csorchestrator.reporters.orchestrator_executor_reporter_markdown import OrchestratorExecutorReporterMarkdown
from csorchestrator.reporters.orchestrator_executor_reporter_print import OrchestratorExecutorReporterPrint
from csorchestrator.reporters.reporter_sink_colorama_print import ReporterSinkColoramaPrint
from csorchestrator.reporters.reporter_sink_colored_print import ReporterSinkColoredPrint


@dataclass
class MockStep(StepBase):
    pass


@dataclass
class MockVisitor(OrchestratorVisitorBase):
    multiline: bool = False

    def init_visit(self) -> None:
        pass

    def end_visit(self, visit_complete: bool) -> None:
        pass

    def begin_phase(self, phase: Phase) -> None:
        pass

    def end_phase(self, phase_complete: bool) -> None:
        pass

    def visit_step_base(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        # By design of the visitor base, visit_step falls back to this
        report = Report()
        reporter_sink.info(f"Visiting {step.name} [I]")
        reporter_sink.warning(f"Visiting {step.name} [W]")
        reporter_sink.error(f"Visiting {step.name} [E]")
        reporter_sink.stdout(f"Visiting {step.name} [cout]")
        reporter_sink.stderr(f"Visiting {step.name} [cerr]")
        if self.multiline:
            reporter_sink.stdout(f"Visiting {step.name} [cout]\nmultiline")
        return report


class MockVisitorReport(OrchestratorVisitorBase):
    def init_visit(self) -> None:
        pass

    def end_visit(self, visit_complete: bool) -> None:
        pass

    def begin_phase(self, phase: Phase) -> None:
        pass

    def end_phase(self, phase_complete: bool) -> None:
        pass

    def visit_step_base(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        # By design of the visitor base, visit_step falls back to this
        report = Report()
        report.append_info(f"Visiting {step.name} [I]")
        report.append_warning(f"Visiting {step.name} [W]")
        report.append_error(f"Visiting {step.name} [E]")
        return report


def test_composite_reporter_prints_twice(capsys: pytest.CaptureFixture[str]) -> None:
    """
    End-to-end test verifying that composing two print reporters results in
    duplicated output (one per reporter).
    """
    # 1. Setup Orchestrator
    orchestrator = Orchestrator()
    phase = Phase(name="Build")
    phase.add_step(MockStep(name="Compile", description="Compile source code"))
    orchestrator.add_phase(phase)

    # 2. Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint()
    rep2 = OrchestratorExecutorReporterPrint()
    rep3 = OrchestratorExecutorReporterDummy()
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3])

    # 3. Execute
    visitor = MockVisitor()
    execute_orchestrator(orchestrator, visitor, composite)

    # 4. Verify Output
    captured = capsys.readouterr().out

    # Every message from the print reporter should appear exactly twice
    # because the composite delegates to both rep1 and rep2.
    expected_messages = [
        "[cout] [init visit]",
        "  [cout] [init phase Build]",
        "    [cout] [init step Compile]",
        "    [info] Visiting Compile [I]",
        "    [warning] Visiting Compile [W]",
        "    [error] Visiting Compile [E]",
        "    [cout] Visiting Compile [cout]",
        "    [cerr] Visiting Compile [cerr]",
        "    [cout] [end step Compile OK]",
        "  [cout] [end phase OK]",
        "[cout] [end visit OK]",
    ]

    for msg in expected_messages:
        assert captured.count(msg) == 2, f"Expected message '{msg}' to appear twice, found {captured.count(msg)}"


def test_composite_reporter_colored_colorama(capsys: pytest.CaptureFixture[str]) -> None:
    # 1. Setup Orchestrator
    orchestrator = Orchestrator()
    phase = Phase(name="Build")
    phase.add_step(MockStep(name="Compile", description="Compile source code"))
    orchestrator.add_phase(phase)

    # 2. Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint(reporter_sink=ReporterSinkColoredPrint())
    rep2 = OrchestratorExecutorReporterPrint(reporter_sink=ReporterSinkColoramaPrint())
    rep3 = OrchestratorExecutorReporterDummy()
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3])

    # 3. Execute
    visitor = MockVisitor(multiline=True)
    execute_orchestrator(orchestrator, visitor, composite)

    # 4. Verify Output
    captured = capsys.readouterr().out

    # just veryfy there is some output
    assert captured.strip() != ""


def test_composite_reporter_markdown(tmp_path: Path) -> None:
    # 1. Setup Orchestrator
    orchestrator = Orchestrator()
    phase = Phase(name="Build")
    phase.add_step(MockStep(name="Compile", description="Compile source code"))
    orchestrator.add_phase(phase)

    md_path = tmp_path / "output.md"

    # 2. Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    reporter = OrchestratorExecutorReporterMarkdown(path=md_path)

    # 3. Execute
    visitor = MockVisitor(multiline=True)
    execute_orchestrator(orchestrator, visitor, reporter)
    reporter.save()

    # 4. Assertions
    assert md_path.exists(), "Markdown file was not created"
    assert md_path.stat().st_size > 0, "Markdown file is empty"

    content = md_path.read_text(encoding="utf-8")
    assert content.lstrip().startswith("#"), "Markdown file does not start with '#'"


def test_composite_reporter_report_pre_execution_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint()
    rep2 = OrchestratorExecutorReporterPrint()
    rep3 = OrchestratorExecutorReporterDummy()
    rep4 = OrchestratorExecutorReporterMarkdown(tmp_path / "output.md")
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3, rep4])

    r = Report()
    r.append_error("Error")
    r.append_warning("Warning")
    r.append_info("Info")

    composite.report_pre_execution_report(r)

    # Verify Output
    captured = capsys.readouterr().out

    # Every message from the print reporter should appear exactly twice
    # because the composite delegates to both rep1 and rep2.
    expected_messages = [
        "  [error] Error",
        "  [warning] Warning",
        "  [info] Info",
    ]

    for msg in expected_messages:
        assert captured.count(msg) == 2, f"Expected message '{msg}' to appear twice, found {captured.count(msg)}"


def test_composite_reporter_report_orchestrator_creation_report(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint()
    rep2 = OrchestratorExecutorReporterPrint()
    rep3 = OrchestratorExecutorReporterDummy()
    rep4 = OrchestratorExecutorReporterMarkdown(tmp_path / "output.md")
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3, rep4])

    r = Report()
    r.append_error("Error")
    r.append_warning("Warning")
    r.append_info("Info")

    composite.report_orchestrator_creation_report(r)

    # Verify Output
    captured = capsys.readouterr().out

    # Every message from the print reporter should appear exactly twice
    # because the composite delegates to both rep1 and rep2.
    expected_messages = [
        "  [error] Error",
        "  [warning] Warning",
        "  [info] Info",
    ]

    for msg in expected_messages:
        assert captured.count(msg) == 2, f"Expected message '{msg}' to appear twice, found {captured.count(msg)}"


def test_composite_reporter_step_with_errors(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Setup Orchestrator
    orchestrator = Orchestrator()
    phase = Phase(name="Build")
    phase.add_step(MockStep(name="Compile", description="Compile source code"))
    orchestrator.add_phase(phase)

    # Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint()
    rep2 = OrchestratorExecutorReporterPrint()
    rep3 = OrchestratorExecutorReporterDummy()
    rep4 = OrchestratorExecutorReporterMarkdown(tmp_path / "output.md")
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3, rep4])

    # Execute
    visitor = MockVisitorReport()
    # use a dummy reporter to avoid printing the execution report at the end, which would interfere with our assertions
    execute_orchestrator(orchestrator, visitor, composite)

    # TODO assert something on print and md


def test_composite_reporter_report_execution_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Setup Orchestrator
    orchestrator = Orchestrator()
    phase = Phase(name="Build")
    phase.add_step(MockStep(name="Compile", description="Compile source code"))
    orchestrator.add_phase(phase)

    # Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint()
    rep2 = OrchestratorExecutorReporterPrint()
    rep3 = OrchestratorExecutorReporterDummy()
    rep4 = OrchestratorExecutorReporterMarkdown(tmp_path / "output.md")
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3, rep4])

    # Execute
    visitor = MockVisitorReport()
    # use a dummy reporter to avoid printing the execution report at the end, which would interfere with our assertions
    report = execute_orchestrator(orchestrator, visitor, OrchestratorExecutorReporterDummy())

    composite.report_execution_report(report)

    # Verify Output
    captured = capsys.readouterr().out

    # Every message from the print reporter should appear exactly twice
    # because the composite delegates to both rep1 and rep2.
    expected_messages = [
        " [info] Visiting Compile [I]",
        " [warning] Visiting Compile [W]",
        " [error] Visiting Compile [E]",
    ]

    for msg in expected_messages:
        assert captured.count(msg) == 2, f"Expected message '{msg}' to appear twice, found {captured.count(msg)}"


def test_composite_reporter_report_execution_description(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Setup Orchestrator
    orchestrator = Orchestrator()
    phase = Phase(name="Build")
    phase.add_step(MockStep(name="Compile", description="Compile source code"))
    orchestrator.add_phase(phase)

    # Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint()
    rep2 = OrchestratorExecutorReporterPrint()
    rep3 = OrchestratorExecutorReporterDummy()
    rep4 = OrchestratorExecutorReporterMarkdown(tmp_path / "output.md")
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3, rep4])

    composite.report_execution_description(orchestrator.extract_minimal_description())

    # Verify Output
    captured = capsys.readouterr().out

    # Every message from the print reporter should appear exactly twice
    # because the composite delegates to both rep1 and rep2.
    expected_messages = ["[cout] Phase: Build", "[cout]   Step: Compile"]

    for msg in expected_messages:
        assert captured.count(msg) == 2, f"Expected message '{msg}' to appear twice, found {captured.count(msg)}"
