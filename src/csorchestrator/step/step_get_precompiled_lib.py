from dataclasses import dataclass

from csorchestrator.ci.github.github_workflow_config import JobOrchestratorMatrixExecution
from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import (
    StepBase,
)
from csorchestrator.foundation.core.report import Report
from csorchestrator.visitors.orchestrator_visitor_github_wf_generator import StepCapabilityGithubWorkflow
from csorchestrator.visitors.orchestrator_visitor_local_executor import StepCapabilityLocalExecution


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
