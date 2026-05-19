from dataclasses import dataclass

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
from csorchestrator.reporters.orchestrator_executor_reporter_print import OrchestratorExecutorReporterPrint


@dataclass
class MockStep(StepBase):
    pass


class MockVisitor(OrchestratorVisitorBase):
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


def test_composite_reporter_report_pre_execution_report(capsys: pytest.CaptureFixture[str]) -> None:
    # Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint()
    rep2 = OrchestratorExecutorReporterPrint()
    rep3 = OrchestratorExecutorReporterDummy()
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3])

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


def test_composite_reporter_report_orchestrator_creation_report(capsys: pytest.CaptureFixture[str]) -> None:
    # Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint()
    rep2 = OrchestratorExecutorReporterPrint()
    rep3 = OrchestratorExecutorReporterDummy()
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3])

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


def test_composite_reporter_report_execution_report(capsys: pytest.CaptureFixture[str]) -> None:
    # Setup Orchestrator
    orchestrator = Orchestrator()
    phase = Phase(name="Build")
    phase.add_step(MockStep(name="Compile", description="Compile source code"))
    orchestrator.add_phase(phase)

    # Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint()
    rep2 = OrchestratorExecutorReporterPrint()
    rep3 = OrchestratorExecutorReporterDummy()
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3])

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


def test_composite_reporter_report_execution_description(capsys: pytest.CaptureFixture[str]) -> None:
    # Setup Orchestrator
    orchestrator = Orchestrator()
    phase = Phase(name="Build")
    phase.add_step(MockStep(name="Compile", description="Compile source code"))
    orchestrator.add_phase(phase)

    # Setup Composite Reporter with two Printing Reporters and a Dummy reporter
    rep1 = OrchestratorExecutorReporterPrint()
    rep2 = OrchestratorExecutorReporterPrint()
    rep3 = OrchestratorExecutorReporterDummy()
    composite = OrchestratorExecutorReporterComposite(reporters=[rep1, rep2, rep3])

    composite.report_execution_description(orchestrator.extract_minimal_description())

    # Verify Output
    captured = capsys.readouterr().out

    # Every message from the print reporter should appear exactly twice
    # because the composite delegates to both rep1 and rep2.
    expected_messages = ["[cout] Phase: Build", "[cout]   Step: Compile"]

    for msg in expected_messages:
        assert captured.count(msg) == 2, f"Expected message '{msg}' to appear twice, found {captured.count(msg)}"
