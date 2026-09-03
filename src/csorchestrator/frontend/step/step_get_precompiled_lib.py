from dataclasses import dataclass

from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import (
    StepBase,
)
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.github_workflow_translation.github_workflow_job_matrix_execution import (
    JobOrchestratorMatrixExecution,
)
from csorchestrator.frontend.github_workflow_translation.orchestrator_visitor_github_wf_generator import (
    StepCapabilityGithubWorkflow,
)
from csorchestrator.frontend.local_execution.context_local_execution import ContextLocalExecution
from csorchestrator.frontend.local_execution.orchestrator_visitor_local_executor import StepCapabilityLocalExecution


@dataclass
class StepGetPrecompiledLibCapabilityGithubWorkflow(StepCapabilityGithubWorkflow):
    step: "StepGetPrecompiledLib"

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report()


@dataclass
class StepGetPrecompiledLibCapabilityLocalExecution(StepCapabilityLocalExecution):
    step: "StepGetPrecompiledLib"

    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report()


@dataclass
class StepGetPrecompiledLib(StepBase):
    def __post_init__(self) -> None:
        self.add_capability(StepGetPrecompiledLibCapabilityGithubWorkflow(self), StepCapabilityGithubWorkflow)
        self.add_capability(StepGetPrecompiledLibCapabilityLocalExecution(self), StepCapabilityLocalExecution)
