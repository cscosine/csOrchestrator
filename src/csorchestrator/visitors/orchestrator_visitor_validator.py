from dataclasses import dataclass, field
from pathlib import Path
from typing import Set

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.step.step_echo_message import StepEchoMessage
from csorchestrator.step.step_get_repository import StepGetRepository, validate_step_get_repository


@dataclass
class OrchestratorVisitorValidator(OrchestratorVisitorBase):
    _colletected_step_get_repository_target_directories: Set[Path] = field(default_factory=set)

    def init_visit(self) -> None:
        pass

    def end_visit(self, visit_complete: bool) -> None:
        pass

    def begin_phase(self, phase: Phase) -> None:
        pass

    def end_phase(self, phase_complete: bool) -> None:
        pass

    def visit_step_base(self, step: StepBase) -> Report:
        return Report().append_warnings(
            f"OrchestratorVisitorValidator cannot handle step f{step.name} of type {type(step).__name__}"
        )

    visit_step = OrchestratorVisitorBase.create_visit_dispatch()

    @visit_step.register
    def _(self, step: StepGetRepository) -> Report:
        r = validate_step_get_repository(step)
        if not r.has_errors():
            target_directory_path = step.target_directory_path()
            if target_directory_path in self._colletected_step_get_repository_target_directories:
                r.append_error(f"target_directory {str(target_directory_path)} is already used by another step")
            else:
                self._colletected_step_get_repository_target_directories.add(target_directory_path)
        return r

    @visit_step.register
    def _(self, step: StepEchoMessage) -> Report:
        # for custom message step, there is no validation
        return Report()
