from dataclasses import dataclass

from csorchestrator.ci.github.github_workflow_config import JobOrchestratorMatrixExecution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase


@dataclass
class OrchestratorVisitorGitHubWorkflowPreparation(OrchestratorVisitorBase):
    wf_job: JobOrchestratorMatrixExecution

    def init_visit(self) -> None:
        pass

    def end_visit(self, visit_complete: bool) -> None:
        pass

    def begin_phase(self, phase: Phase) -> None:
        pass

    def end_phase(self, phase_complete: bool) -> None:
        pass

    def visit_step(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        return step.to_githubwf(self.wf_job, reporter_sink)
