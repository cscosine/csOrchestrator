from dataclasses import dataclass, field
from pathlib import Path

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.step.step_cmake_command import StepCMakeWorkflow, validate_step_cmake_workflow
from csorchestrator.step.step_echo_message import StepEchoMessage
from csorchestrator.step.step_get_repository import StepGetRepository, validate_step_get_repository


@dataclass
class OrchestratorVisitorValidator(OrchestratorVisitorBase):
    _collected_step_get_repository_target_directories: set[Path] = field(default_factory=set)

    def init_visit(self) -> None:
        pass

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
    def _(self, step: StepGetRepository, reporter_sink: ReporterSinkBase) -> Report:
        r = validate_step_get_repository(step)
        if not r.has_errors():
            target_directory_path = step.resolved_target_directory_path()
            if target_directory_path in self._collected_step_get_repository_target_directories:
                r.append_error(f"target_directory {str(target_directory_path)} is already used by another step")
            else:
                self._collected_step_get_repository_target_directories.add(target_directory_path)
        return r

    @visit_step.register
    def _(self, step: StepCMakeWorkflow, reporter_sink: ReporterSinkBase) -> Report:
        return validate_step_cmake_workflow(step)

    @visit_step.register
    def _(self, step: StepEchoMessage, reporter_sink: ReporterSinkBase) -> Report:
        # for custom message step, there is no validation
        return Report()
