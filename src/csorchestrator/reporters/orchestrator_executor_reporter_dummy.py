from dataclasses import dataclass

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.orchestrator.orchestrator_minimal_description import OrchestratorExecutorMinimalDescription
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorExecutorVisitReports
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.reporters.reporter_sink_dummy import ReporterSinkDummy


@dataclass
class OrchestratorExecutorReporterDummy(OrchestratorExecutorReporterBase):
    def on_init_visit(self) -> None:
        pass

    def on_end_visit(self, visit_complete: bool) -> None:
        pass

    def finalize_execution(self) -> None:
        pass

    def on_begin_phase(self, phase: Phase) -> None:
        pass

    def on_end_phase(self, phase_complete: bool) -> None:
        pass

    def create_sink_on_begin_visit_step(self, step: StepBase) -> ReporterSinkBase:
        return ReporterSinkDummy()

    def on_end_visit_step(self, step: StepBase, report: Report) -> None:
        pass

    def report_orchestrator_creation_report(self, report: Report) -> None:
        pass

    def report_execution_description(self, execution_description: OrchestratorExecutorMinimalDescription) -> None:
        pass

    def report_pre_execution_report(self, report: Report) -> None:
        pass

    def report_validation_report(self, report: OrchestratorExecutorVisitReports) -> None:
        pass

    def report_execution_report(self, report: OrchestratorExecutorVisitReports) -> None:
        pass

    def report_start_execution(self, exec_desc: str) -> None:
        pass

    def report_skip_execution(self, exec_desc: str) -> None:
        pass
