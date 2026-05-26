from dataclasses import dataclass, field
from typing import Callable, Optional, TypeAlias

from csorchestrator.context.context_compiler_generator import ContextCompilerGenerator
from csorchestrator.context.context_os_architecture import ContextOsArchitecture
from csorchestrator.context.execution_matrix_base import OrchestratorExecutionMatrixBase
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


CompilerGeneratorFunc = Callable[[ContextOsArchitecture], ContextCompilerGenerator | None]


def default_context_compiler_generator_func_none(
    os_architecture: ContextOsArchitecture,
) -> Optional[ContextCompilerGenerator]:
    return None


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
    execution_matrix: OrchestratorExecutionMatrixBase | None = None
    _get_context_compiler_generator_func: CompilerGeneratorFunc = default_context_compiler_generator_func_none

    def add_phase(self, phase: Phase) -> "Orchestrator":
        self.phases.append(phase)
        return self

    def create_phase(self, phase_name: str) -> Phase:
        phase = Phase(phase_name)
        self.phases.append(phase)
        return phase

    def set_execution_matrix(self, matrix: OrchestratorExecutionMatrixBase) -> "Orchestrator":
        self.execution_matrix = matrix
        return self

    def set_context_compiler_generator_func(self, func: CompilerGeneratorFunc) -> None:
        self._get_context_compiler_generator_func = func

    def get_default_context_compiler_generator(
        self, os_architecture: ContextOsArchitecture
    ) -> ContextCompilerGenerator | None:
        return self._get_context_compiler_generator_func(os_architecture)

    def extract_minimal_description(self) -> OrchestratorExecutorMinimalDescription:
        ret = OrchestratorExecutorMinimalDescription()
        for phase in self.phases:
            phase_desc = PhaseNameWithStepNames(phase.name)
            for step in phase.steps:
                phase_desc.step_names.append(step.name)
            ret.phases_and_steps.append(phase_desc)
        if self.execution_matrix is None:
            ret.matrix_description = []
        else:
            ret.matrix_description = self.execution_matrix.to_list_string_description()
        return ret


OptionalOrchestratorWithReport: TypeAlias = OptionalResultWithReport[Orchestrator]
