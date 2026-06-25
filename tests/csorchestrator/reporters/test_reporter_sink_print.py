from dataclasses import dataclass

import pytest

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.domain.orchestrator.orchestrator_executor import execute_orchestrator
from csorchestrator.domain.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.domain.orchestrator.phase import Phase
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import (
    JobOrchestratorMatrixExecution,
    StepBase,
    StepValidatorBase,
    StepValidatorNoOp,
)
from csorchestrator.execution.factory import create_orchestrator_factory
from csorchestrator.foundation.core.report import Report
from csorchestrator.reporters.orchestrator_executor_reporter_print import OrchestratorExecutorReporterPrint
from csorchestrator.reporters.reporter_sink_print import ReporterSinkPrint


@dataclass
class MockStep(StepBase):
    name: str
    should_fail: bool = False

    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report()

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report()

    @classmethod
    def createValidator(cls) -> StepValidatorBase:
        return StepValidatorNoOp()


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
        return self.visit_step(step, reporter_sink)

    def visit_step(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        assert isinstance(step, MockStep)
        report = Report()
        report.append_warning(f"Warning in {step.name}")
        report.append_info(f"Info in {step.name}")
        reporter_sink.info(f"Executing {step.name}")
        if step.should_fail:
            report.append_error(f"Error in {step.name}")
            reporter_sink.error(f"Failed {step.name}")
        return report


def test_reporter_sink_print_direct_methods(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify that ReporterSinkPrint correctly prefixes and outputs text."""
    sink = ReporterSinkPrint()
    sink.stdout("stdout message")
    sink.stderr("stderr message")
    sink.info("info message")
    sink.warning("warning message")
    sink.error("error message")

    captured = capsys.readouterr()
    assert "[cout] stdout message\n" in captured.out
    assert "[cerr] stderr message\n" in captured.out
    assert "[info] info message\n" in captured.out
    assert "[warning] warning message\n" in captured.out
    assert "[error] error message\n" in captured.out


def test_reporter_sink_print_indentation(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify indentation levels in ReporterSinkPrint."""
    sink = ReporterSinkPrint()
    sink.stdout("level 0")
    sink.increase_indentation()
    sink.stdout("level 1")
    sink.increase_indentation()
    sink.stdout("level 2")
    sink.stdout("level 2b\nmultiline")
    sink.decrease_indentation()
    sink.stdout("back to 1")
    sink.reset_indentation()
    sink.stdout("back to 0")

    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert lines[0] == "[cout] level 0"
    assert lines[1] == "  [cout] level 1"
    assert lines[2] == "    [cout] level 2"
    assert lines[3] == "    [cout] level 2b"
    assert lines[4] == "           multiline"
    assert lines[5] == "  [cout] back to 1"
    assert lines[6] == "[cout] back to 0"


def test_orchestrator_executor_reporter_print_success_flow(capsys: pytest.CaptureFixture[str]) -> None:
    """End-to-end test of the printing reporter via execute_orchestrator on success."""
    orchestrator = create_orchestrator_factory("myName", "0.0.0", "exec-job")
    phase = Phase(name="Setup")
    phase.add_step(MockStep(name="StepA", description=""))
    orchestrator.add_phase(phase)

    reporter = OrchestratorExecutorReporterPrint()
    visitor = MockVisitor()

    execute_orchestrator(orchestrator, visitor, reporter)

    captured = capsys.readouterr()
    expected_parts = [
        "[cout] [init visit]",
        "  [cout] [init phase Setup]",
        "    [cout] [init step StepA]",
        "    [info] Executing StepA",
        "    [cout] [end step StepA OK]",
        "  [cout] [end phase OK]",
        "[cout] [end visit OK]",
    ]
    for part in expected_parts:
        assert part in captured.out


def test_orchestrator_executor_reporter_print_failure_flow(capsys: pytest.CaptureFixture[str]) -> None:
    """End-to-end test of the printing reporter via execute_orchestrator on failure."""
    orchestrator = create_orchestrator_factory("myName", "0.0.0", "exec-job")
    phase = Phase(name="Execution")
    phase.add_step(MockStep(name="FailingStep", description="", should_fail=True))
    orchestrator.add_phase(phase)

    reporter = OrchestratorExecutorReporterPrint()
    visitor = MockVisitor()

    execute_orchestrator(orchestrator, visitor, reporter)

    captured = capsys.readouterr()
    assert "    [error] Failed FailingStep" in captured.out
    assert "    [cout] [end step FailingStep FAIL]" in captured.out
    assert "  [cout] [end phase FAIL]" in captured.out
    assert "[cout] [end visit FAIL]" in captured.out
