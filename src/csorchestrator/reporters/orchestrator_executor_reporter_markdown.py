from dataclasses import dataclass, field
from pathlib import Path

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import OrchestratorExecutorMinimalDescription
from csorchestrator.orchestrator.orchestrator_executor import flatten_orchestrator_executor_visit_reports
from csorchestrator.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorExecutorVisitReports
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.reporters.report_reporter import repo_to_reporter_sink
from csorchestrator.reporters.reporter_sink_markdown_file import ReporterSinkMarkdown


@dataclass
class OrchestratorExecutorReporterMarkdown(OrchestratorExecutorReporterBase):
    path: Path
    sink: ReporterSinkMarkdown = field(init=False)

    def __post_init__(self) -> None:
        self.sink = ReporterSinkMarkdown()

    # ---------------- VISIT ----------------

    def on_init_visit(self) -> None:
        self.sink.lines.append("# Orchestrator Execution Report\n")

    def on_end_visit(self, visit_complete: bool) -> None:
        status = "SUCCESS" if visit_complete else "FAILURE"
        self.sink.lines.append(f"\n## End Visit: {status}\n")
        self.save()

    # ---------------- PHASE ----------------

    def on_begin_phase(self, phase: Phase) -> None:
        self.sink.lines.append(f"\n## Phase: {phase.name}\n")

    def on_end_phase(self, phase_complete: bool) -> None:
        self.sink.lines.append(f"\n**Phase result:** {'OK' if phase_complete else 'FAIL'}\n")

    # ---------------- STEP ----------------

    def create_sink_on_begin_visit_step(self, step: StepBase) -> ReporterSinkBase:
        self.sink.lines.append(f"\n### Step: {step.name}\n")
        self.sink.increase_indentation()
        return self.sink

    def on_end_visit_step(self, step: StepBase, report: Report) -> None:
        if report.has_errors():
            self.sink.lines.append(f"❌ Step {step.name} FAILED\n")
        else:
            self.sink.lines.append(f"✔ Step {step.name} OK\n")

        repo_to_reporter_sink(report, self.sink)
        self.sink.decrease_indentation()

    # ---------------- CREATION ----------------

    def report_orchestrator_creation_report(self, report: Report) -> None:
        self.sink.lines.append("## Creation Report\n")
        repo_to_reporter_sink(report, self.sink)

    # ---------------- EXECUTION DESCRIPTION ----------------

    def report_execution_description(
        self,
        execution_description: OrchestratorExecutorMinimalDescription,
    ) -> None:
        self.sink.lines.append("## Execution Description\n")

        for phase_desc in execution_description.phases_and_steps:
            self.sink.lines.append(f"### Phase: {phase_desc.phase_name}")
            for step_name in phase_desc.step_names:
                self.sink.lines.append(f"- Step: {step_name}")

        if len(execution_description.matrix_description) > 0:
            self.sink.lines.append("### Execution Matrix")
            for line in execution_description.matrix_description:
                self.sink.lines.append(f"- {line}")

    # ---------------- PRE EXECUTION ----------------

    def report_pre_execution_report(self, report: Report) -> None:
        self.sink.lines.append("## Pre-Execution Report\n")
        repo_to_reporter_sink(report, self.sink)

    # ---------------- EXECUTION REPORT ----------------

    def report_execution_report(self, reportVisit: OrchestratorExecutorVisitReports) -> None:
        self.sink.lines.append("## Execution Report\n")

        report = flatten_orchestrator_executor_visit_reports(reportVisit)
        repo_to_reporter_sink(report, self.sink)

    # ---------------- SAVE ----------------

    def save(self) -> None:
        self.path.write_text("\n".join(self.sink.lines), encoding="utf-8")
