from dataclasses import dataclass, field

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
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
        self.reporter_sink.decrease_indentation()
