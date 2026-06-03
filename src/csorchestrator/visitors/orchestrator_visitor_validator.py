from dataclasses import dataclass, field

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.step.step_cmake_command import StepCMakeWorkflow, validate_step_cmake_workflow
from csorchestrator.step.step_create_archives import StepCreateArchives, validate_step_create_archives
from csorchestrator.step.step_custom_command import StepCustomCommand, validate_step_custom_command
from csorchestrator.step.step_echo_message import StepEchoMessage
from csorchestrator.step.step_get_repository import (
    StepGetRepositoryGitHub,
    StepGetRepositoryValidator,
)
from csorchestrator.step.step_get_versions_from_cmake_config_package_version import (
    StepGetVersionsFromCMakeConfigPackageVersion,
    validate_step_get_versions_from_cmake_config_package_version,
)
from csorchestrator.step.step_upload_artifacts import StepUploadArtifacts, validate_step_upload_artifacts


@dataclass
class OrchestratorVisitorValidator(OrchestratorVisitorBase):
    step_get_repository_validator: StepGetRepositoryValidator = field(default_factory=StepGetRepositoryValidator)

    def init_visit(self) -> None:
        self.step_get_repository_validator.clear()

    def end_visit(self, visit_complete: bool) -> None:
        pass

    def begin_phase(self, phase: Phase) -> None:
        pass

    def end_phase(self, phase_complete: bool) -> None:
        pass

    def visit_step_base(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        return Report().append_warning(
            f"OrchestratorVisitorValidator cannot handle step {step.name} of type {type(step).__name__}"
        )

    visit_step = OrchestratorVisitorBase.create_visit_dispatch()

    @visit_step.register
    def _(self, step: StepGetRepositoryGitHub, reporter_sink: ReporterSinkBase) -> Report:
        return self.step_get_repository_validator.validate_step_get_repository(step)

    @visit_step.register
    def _(self, step: StepCMakeWorkflow, reporter_sink: ReporterSinkBase) -> Report:
        return validate_step_cmake_workflow(step)

    @visit_step.register
    def _(self, step: StepEchoMessage, reporter_sink: ReporterSinkBase) -> Report:
        # for custom message step, there is no validation
        return Report()

    @visit_step.register
    def _(self, step: StepGetVersionsFromCMakeConfigPackageVersion, reporter_sink: ReporterSinkBase) -> Report:
        return validate_step_get_versions_from_cmake_config_package_version(step)

    @visit_step.register
    def _(self, step: StepCreateArchives, reporter_sink: ReporterSinkBase) -> Report:
        return validate_step_create_archives(step)

    @visit_step.register
    def _(self, step: StepUploadArtifacts, reporter_sink: ReporterSinkBase) -> Report:
        return validate_step_upload_artifacts(step)

    @visit_step.register
    def _(self, step: StepCustomCommand, reporter_sink: ReporterSinkBase) -> Report:
        return validate_step_custom_command(step)
