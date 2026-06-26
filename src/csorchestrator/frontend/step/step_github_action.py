from dataclasses import dataclass, field

from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import (
    StepBase,
)
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.github_workflow_translation.github_workflow_config import JobOrchestratorMatrixExecution
from csorchestrator.frontend.github_workflow_translation.github_workflow_steps_transations import StepGitHubAction
from csorchestrator.frontend.github_workflow_translation.orchestrator_visitor_github_wf_generator import (
    StepCapabilityGithubWorkflow,
)
from csorchestrator.frontend.step.step_custom_command import get_if_str


@dataclass
class StepAddGitHubActionCapabilityGithubWorkflow(StepCapabilityGithubWorkflow):
    step: "StepAddGitHubAction"

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return step_add_github_action_to_githubwf(self.step, wf_job, reporter_sink)


@dataclass
class StepAddGitHubAction(StepBase):
    name: str
    uses: str
    with_list: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.add_capability(StepAddGitHubActionCapabilityGithubWorkflow(self), StepCapabilityGithubWorkflow)


def step_add_github_action_to_githubwf(
    step: StepAddGitHubAction, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:
    wf_job.steps.append(
        StepGitHubAction(
            name=step.name,
            uses=step.uses,
            if_str=get_if_str(step),
            with_list=step.with_list,
        )
    )
    return Report()
