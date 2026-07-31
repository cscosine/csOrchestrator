from dataclasses import dataclass, field

from csorchestrator.domain.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.domain.orchestrator.orchestrator_minimal_description import OrchestratorExecutorMinimalDescription
from csorchestrator.domain.orchestrator.orchestrator_visitor_base import OrchestratorExecutorVisitReports
from csorchestrator.domain.orchestrator.phase import Phase
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import StepBase
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.reporters.reporter_sink_composite import ReporterSinkComposite


@dataclass
class OrchestratorExecutorReporterComposite(OrchestratorExecutorReporterBase):
    reporters: list[OrchestratorExecutorReporterBase] = field(default_factory=list)

    def on_init_visit(self) -> None:
        for r in self.reporters:
            r.on_init_visit()

    def on_end_visit(self, visit_complete: bool) -> None:
        for r in self.reporters:
            r.on_end_visit(visit_complete)

    def finalize_execution(self) -> None:
        for r in self.reporters:
            r.finalize_execution()

    def report_postexecution(self, report: Report) -> None:
        for r in self.reporters:
            r.report_postexecution(report)

    def on_begin_phase(self, phase: Phase) -> None:
        for r in self.reporters:
            r.on_begin_phase(phase)

    def on_end_phase(self, phase_complete: bool) -> None:
        for r in self.reporters:
            r.on_end_phase(phase_complete)

    def create_sink_on_begin_visit_step(self, step: StepBase) -> ReporterSinkBase:
        sinks: list[ReporterSinkBase] = []
        for r in self.reporters:
            sinks.append(r.create_sink_on_begin_visit_step(step))
        return ReporterSinkComposite(sinks)

    def on_end_visit_step(self, step: StepBase, report: Report) -> None:
        for r in self.reporters:
            r.on_end_visit_step(step, report)

    def report_orchestrator_creation_report(self, report: Report) -> None:
        for r in self.reporters:
            r.report_orchestrator_creation_report(report)

    def report_execution_description(self, execution_description: OrchestratorExecutorMinimalDescription) -> None:
        for r in self.reporters:
            r.report_execution_description(execution_description)

    def report_pre_execution_report(self, report: Report) -> None:
        for r in self.reporters:
            r.report_pre_execution_report(report)

    def report_validation_report(self, report: OrchestratorExecutorVisitReports) -> None:
        for r in self.reporters:
            r.report_validation_report(report)

    def report_execution_report(self, report: OrchestratorExecutorVisitReports) -> None:
        for r in self.reporters:
            r.report_execution_report(report)

    def report_start_execution(self, exec_desc: str) -> None:
        for r in self.reporters:
            r.report_start_execution(exec_desc)

    def report_skip_execution(self, exec_desc: str) -> None:
        for r in self.reporters:
            r.report_skip_execution(exec_desc)
