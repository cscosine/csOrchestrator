from dataclasses import dataclass, field
from typing import TypeAlias

from csorchestrator.context.context_os_architecture_compiler_generator import ExecutionMatrixOsArchCompilerGenerator
from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.orchestrator.phase import Phase


@dataclass(frozen=True)
class PhaseNameWithStepNames:
    phase_name: str
    step_names: list[str] = field(default_factory=list)


@dataclass
class OrchestratorExecutorMinimalDescription:
    phases_and_steps: list[PhaseNameWithStepNames] = field(
        default_factory=list
    )  # a list of phases names and list of step names
    matrix_description: list[str] = field(default_factory=list)  # a list of string describing the execution matrix


@dataclass
class Orchestrator:
    # - create phase (e.g. setup / config / build)
    # per each phase allows to add
    #   - run custom command
    #   - get precompiled lib
    #   - add_repository
    #   - add local folder as src
    #   - run cmake workflow / individual steps (config / build / test / install)

    phases: list[Phase] = field(default_factory=list)
    _execution_matrix: ExecutionMatrixOsArchCompilerGenerator | None = None

    def add_phase(self, phase: Phase) -> "Orchestrator":
        self.phases.append(phase)
        return self

    def create_phase(self, phase_name: str) -> Phase:
        phase = Phase(phase_name)
        self.phases.append(phase)
        return phase

    def set_execution_matrix(self, matrix: ExecutionMatrixOsArchCompilerGenerator) -> "Orchestrator":
        self._execution_matrix = matrix
        return self

    def get_execution_matrix(self) -> ExecutionMatrixOsArchCompilerGenerator | None:
        return self._execution_matrix

    def extract_minimal_description(self) -> OrchestratorExecutorMinimalDescription:
        ret = OrchestratorExecutorMinimalDescription()
        for phase in self.phases:
            phase_desc = PhaseNameWithStepNames(phase.name)
            for step in phase.steps:
                phase_desc.step_names.append(step.name)
            ret.phases_and_steps.append(phase_desc)
        if self._execution_matrix is None:
            ret.matrix_description = []
        else:
            ret.matrix_description = self._execution_matrix.to_list_string_description()
        return ret


OptionalOrchestratorWithReport: TypeAlias = OptionalResultWithReport[Orchestrator]
