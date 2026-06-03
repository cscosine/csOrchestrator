from dataclasses import dataclass

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.step.step_cmake_command import (
    StepCMakeWorkflow,
    execute_step_cmake_workflow,
)
from csorchestrator.step.step_create_archives import StepCreateArchives, execute_step_create_archives
from csorchestrator.step.step_custom_command import (
    StepCustomCommand,
    execute_step_custom_command,
)
from csorchestrator.step.step_echo_message import StepEchoMessage, execute_step_echo_message
from csorchestrator.step.step_get_repository import StepGetRepositoryGitHub, execute_step_get_repository
from csorchestrator.step.step_get_versions_from_cmake_config_package_version import (
    StepGetVersionsFromCMakeConfigPackageVersion,
    execute_step_get_versions_from_cmake_config_package_version,
)
from csorchestrator.step.step_upload_artifacts import StepUploadArtifacts, execute_step_upload_artifacts


@dataclass
class OrchestratorVisitorLocalExecutor(OrchestratorVisitorBase):
    context: ContextLocalExecution

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
            f"OrchestratorVisitorLocalExecutor cannot handle step {step.name} of type {type(step).__name__}"
        )

    visit_step = OrchestratorVisitorBase.create_visit_dispatch()

    @visit_step.register
    def _(self, step: StepGetRepositoryGitHub, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_get_repository(step, self.context, reporter_sink)

    @visit_step.register
    def _(self, step: StepCMakeWorkflow, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_cmake_workflow(step, self.context, reporter_sink)

    @visit_step.register
    def _(self, step: StepEchoMessage, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_echo_message(step, self.context, reporter_sink)

    @visit_step.register
    def _(self, step: StepGetVersionsFromCMakeConfigPackageVersion, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_get_versions_from_cmake_config_package_version(step, self.context, reporter_sink)

    @visit_step.register
    def _(self, step: StepCreateArchives, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_create_archives(step, self.context, reporter_sink)

    @visit_step.register
    def _(self, step: StepUploadArtifacts, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_upload_artifacts(step, self.context, reporter_sink)

    @visit_step.register
    def _(self, step: StepCustomCommand, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_custom_command(step, self.context, reporter_sink)
