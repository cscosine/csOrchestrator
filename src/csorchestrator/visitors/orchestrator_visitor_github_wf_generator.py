from dataclasses import dataclass

from csorchestrator.ci.github.github_workflow_config import JobDescription
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.step.step_cmake_command import StepCMakeWorkflow
from csorchestrator.step.step_echo_message import StepEchoMessage
from csorchestrator.step.step_get_repository import StepGetRepositoryGitHub, step_get_repository_to_githubwf


@dataclass
class OrchestratorVisitorGithubWorkflowPreparation(OrchestratorVisitorBase):
    wf_job: JobDescription

    def init_visit(self) -> None:
        pass

    def end_visit(self, visit_complete: bool) -> None:
        pass

    def begin_phase(self, phase: Phase) -> None:
        pass

    def end_phase(self, phase_complete: bool) -> None:
        pass

    def visit_step_base(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        return Report().append_error(
            f"OrchestratorVisitorGithubWorkflowPreparation cannot handle step {step.name} of type {type(step).__name__}"
        )

    visit_step = OrchestratorVisitorBase.create_visit_dispatch()

    @visit_step.register
    def _(self, step: StepGetRepositoryGitHub, reporter_sink: ReporterSinkBase) -> Report:
        return step_get_repository_to_githubwf(step, self.wf_job, reporter_sink)

    @visit_step.register
    def _(self, step: StepCMakeWorkflow, reporter_sink: ReporterSinkBase) -> Report:
        # return step_cmake_workflow_to_githubwf(step, self.wf_job, reporter_sink)
        return Report()  # TODO

    @visit_step.register
    def _(self, step: StepEchoMessage, reporter_sink: ReporterSinkBase) -> Report:
        # return step_echo_message_to_githubwf(step, self.wf_job, reporter_sink)
        return Report()  # TODO
