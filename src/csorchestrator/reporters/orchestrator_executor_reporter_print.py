from dataclasses import dataclass, field

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import OrchestratorExecutorMinimalDescription
from csorchestrator.orchestrator.orchestrator_executor import flatten_orchestrator_executor_visit_reports
from csorchestrator.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorExecutorVisitReports
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.reporters.reporter_sink_print import ReporterSinkPrint


@dataclass
class OrchestratorExecutorReporterPrint(OrchestratorExecutorReporterBase):
    reporter_sink: ReporterSinkPrint = field(default_factory=ReporterSinkPrint)

    def on_init_visit(self) -> None:
        self.reporter_sink.reset_indentation()
        self.reporter_sink.stdout("[init visit]")

    def on_end_visit(self, visit_complete: bool) -> None:
        if visit_complete:
            self.reporter_sink.stdout("[end visit OK]")
        else:
            self.reporter_sink.stdout("[end visit FAIL]")
        self.reporter_sink.reset_indentation()

    def on_begin_phase(self, phase: Phase) -> None:
        self.reporter_sink.increase_indentation()
        self.reporter_sink.stdout(f"[init phase {phase.name}]")

    def on_end_phase(self, phase_complete: bool) -> None:
        if phase_complete:
            self.reporter_sink.stdout("[end phase OK]")
        else:
            self.reporter_sink.stdout("[end phase FAIL]")
        self.reporter_sink.decrease_indentation()

    def create_sink_on_begin_visit_step(self, step: StepBase) -> ReporterSinkBase:
        self.reporter_sink.increase_indentation()
        self.reporter_sink.stdout(f"[init step {step.name}]")
        return self.reporter_sink

    def on_end_visit_step(self, step: StepBase, report: Report) -> None:
        if not report.has_errors():
            self.reporter_sink.stdout(f"[end step {step.name} OK]")
        else:
            self.reporter_sink.stdout(f"[end step {step.name} FAIL]")

        self.reporter_sink.stdout(f"[{step.name} REPORT]")
        self.reporter_sink.increase_indentation()
        for m in report.errors:
            self.reporter_sink.stdout(f"[ERROR] {m}")
        for m in report.warnings:
            self.reporter_sink.stdout(f"[WARNING] {m}")
        for m in report.infos:
            self.reporter_sink.stdout(f"[INFO] {m}")
        self.reporter_sink.decrease_indentation()

        # end step indent
        self.reporter_sink.decrease_indentation()

    def report_orchestrator_creation_report(self, report: Report) -> None:
        self.reporter_sink.stdout("[Creation Report]")
        self.reporter_sink.increase_indentation()
        for m in report.errors:
            self.reporter_sink.stdout(f"[ERROR] {m}")
        for m in report.warnings:
            self.reporter_sink.stdout(f"[WARNING] {m}")
        for m in report.infos:
            self.reporter_sink.stdout(f"[INFO] {m}")
        self.reporter_sink.decrease_indentation()

    def report_execution_description(self, execution_description: OrchestratorExecutorMinimalDescription) -> None:
        for phase_desc in execution_description:
            self.reporter_sink.stdout(f"Phase: {phase_desc.phase_name}")
            for step_name in phase_desc.step_names:
                self.reporter_sink.stdout(f"  Step: {step_name}")

    def report_pre_execution_report(self, report: Report) -> None:
        self.reporter_sink.stdout("[Pre-Execution Report]")
        self.reporter_sink.increase_indentation()
        for m in report.errors:
            self.reporter_sink.stdout(f"[ERROR] {m}")
        for m in report.warnings:
            self.reporter_sink.stdout(f"[WARNING] {m}")
        for m in report.infos:
            self.reporter_sink.stdout(f"[INFO] {m}")
        self.reporter_sink.decrease_indentation()

    def report_execution_report(self, reportVisit: OrchestratorExecutorVisitReports) -> None:
        self.reporter_sink.stdout("[Execution Report]")
        self.reporter_sink.increase_indentation()
        report = flatten_orchestrator_executor_visit_reports(reportVisit)
        for m in report.errors:
            self.reporter_sink.stdout(f"[ERROR] {m}")
        for m in report.warnings:
            self.reporter_sink.stdout(f"[WARNING] {m}")
        for m in report.infos:
            self.reporter_sink.stdout(f"[INFO] {m}")
        self.reporter_sink.decrease_indentation()
