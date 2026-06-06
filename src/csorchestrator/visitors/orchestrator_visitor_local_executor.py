from dataclasses import dataclass
from typing import Callable, TypeVar

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.step.step_cmake_command import StepCMakeWorkflow, execute_step_cmake_workflow
from csorchestrator.step.step_create_archives import StepCreateArchives, execute_step_create_archives
from csorchestrator.step.step_custom_command import (
    StepBashScriptCommand,
    StepWinPSCommand,
    execute_step_custom_command,
    execute_step_win_ps_command,
)
from csorchestrator.step.step_echo_message import StepEchoMessage, execute_step_echo_message
from csorchestrator.step.step_get_repository import StepGetRepositoryGitHub, execute_step_get_repository
from csorchestrator.step.step_get_versions_from_cmake_config_package_version import (
    StepGetVersionsFromCMakeConfigPackageVersion,
    execute_step_get_versions_from_cmake_config_package_version,
)
from csorchestrator.step.step_upload_artifacts import StepUploadArtifacts, execute_step_upload_artifacts
from csorchestrator.step.step_utils import StepExecuteOnlyOn, StepExecuteOnlyOncePerMatrix, StepSkipExecutionOnLocal


@dataclass
class OrchestratorVisitorLocalExecutor(OrchestratorVisitorBase):
    context: ContextLocalExecution
    _current_phase_name: str | None = None

    def init_visit(self) -> None:
        pass

    def end_visit(self, visit_complete: bool) -> None:
        pass

    def begin_phase(self, phase: Phase) -> None:
        self._current_phase_name = phase.name

    def end_phase(self, phase_complete: bool) -> None:
        self._current_phase_name = None

    def visit_step_base(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        return Report().append_error(
            f"OrchestratorVisitorLocalExecutor cannot handle step {step.name} of type {type(step).__name__}"
        )

    visit_step = OrchestratorVisitorBase.create_visit_dispatch()

    def should_execute_step(self, step: StepBase) -> None | str:  # None is non expected error
        if self._current_phase_name is None:
            return "Failed to determine current phase - unexpected error in should_execute_step"

        # manage skip on local execution
        if step.get_extra(StepSkipExecutionOnLocal) is not None:
            return "Step is marked to be skipped on local execution"

        # manage skip on non matching OS
        execute_only_on_extra = step.get_extra(StepExecuteOnlyOn)
        if execute_only_on_extra is not None:
            result = execute_only_on_extra.evaluate_local_exec(self.context)
            if result is not None:
                return result

        # manage single execution per matrix
        exec_only_one = step.get_extra(StepExecuteOnlyOncePerMatrix)
        if exec_only_one is not None:
            result = exec_only_one.evaluate_local_exec(self.context, self._current_phase_name, step.name)
            if result is not None:
                return result
        return None

    TStep = TypeVar("TStep", bound=StepBase)

    def _run_step(
        self,
        executor: Callable[[TStep, ContextLocalExecution, ReporterSinkBase], Report],
        step: TStep,
        reporter_sink: ReporterSinkBase,
    ) -> Report:
        skip_reason = self.should_execute_step(step)
        if skip_reason is not None:
            return Report().append_info(
                f"skipping execution of step {step.name} of type {type(step).__name__} since {skip_reason}"
            )

        return executor(step, self.context, reporter_sink)

    @visit_step.register
    def _(self, step: StepGetRepositoryGitHub, reporter_sink: ReporterSinkBase) -> Report:
        return self._run_step(execute_step_get_repository, step, reporter_sink)

    @visit_step.register
    def _(self, step: StepCMakeWorkflow, reporter_sink: ReporterSinkBase) -> Report:
        return self._run_step(execute_step_cmake_workflow, step, reporter_sink)

    @visit_step.register
    def _(self, step: StepEchoMessage, reporter_sink: ReporterSinkBase) -> Report:
        return self._run_step(execute_step_echo_message, step, reporter_sink)

    @visit_step.register
    def _(self, step: StepGetVersionsFromCMakeConfigPackageVersion, reporter_sink: ReporterSinkBase) -> Report:
        return self._run_step(execute_step_get_versions_from_cmake_config_package_version, step, reporter_sink)

    @visit_step.register
    def _(self, step: StepCreateArchives, reporter_sink: ReporterSinkBase) -> Report:
        return self._run_step(execute_step_create_archives, step, reporter_sink)

    @visit_step.register
    def _(self, step: StepUploadArtifacts, reporter_sink: ReporterSinkBase) -> Report:
        return self._run_step(execute_step_upload_artifacts, step, reporter_sink)

    @visit_step.register
    def _(self, step: StepBashScriptCommand, reporter_sink: ReporterSinkBase) -> Report:
        return self._run_step(execute_step_custom_command, step, reporter_sink)

    @visit_step.register
    def _(self, step: StepWinPSCommand, reporter_sink: ReporterSinkBase) -> Report:
        return self._run_step(execute_step_win_ps_command, step, reporter_sink)
