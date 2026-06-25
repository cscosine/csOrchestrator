from dataclasses import dataclass, field

from csorchestrator.ci.github.github_workflow_steps_transations import StepGitHubAction
from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import (
    JobOrchestratorMatrixExecution,
    StepBase,
    StepValidatorBase,
    StepValidatorNoOp,
)
from csorchestrator.foundation.core.report import Report
from csorchestrator.step.step_custom_command import get_if_str


@dataclass
class StepAddGitHubAction(StepBase):
    name: str
    uses: str
    with_list: list[str] = field(default_factory=list)

    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_add_github_action(self, context, reporter_sink)

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return step_add_github_action_to_githubwf(self, wf_job, reporter_sink)

    @classmethod
    def createValidator(cls) -> StepValidatorBase:
        return StepValidatorNoOp()


def execute_step_add_github_action(
    repo_step: StepAddGitHubAction, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    return Report().append_info("StepAddGitHubAction is no-op in local execution")


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
