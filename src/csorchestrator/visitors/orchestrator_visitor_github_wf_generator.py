from dataclasses import dataclass

from csorchestrator.domain.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.domain.orchestrator.phase import Phase
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import StepBase, StepCapability
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.github.github_workflow_config import JobOrchestratorMatrixExecution


@dataclass
class StepCapabilityGithubWorkflow(StepCapability):
    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report().append_error("StepCapabilityGithubWorkflow.to_githubwf need to be imlemented in subclasses")


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
        capability = step.get_capability(StepCapabilityGithubWorkflow)
        if capability is None:
            return Report().append_info(f"skip step {step.name} because it does not support github workflow")
        return capability.to_githubwf(self.wf_job, reporter_sink)
