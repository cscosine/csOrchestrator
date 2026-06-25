from dataclasses import dataclass, field

from csorchestrator.context.context_os_architecture_compiler_generator import (
    ContextOsArchitectureCompilerGenerator,
    ExecutionMatrixOsArchCompilerGenerator,
)
from csorchestrator.domain.orchestrator.orchestrator_minimal_description import (
    OrchestratorExecutorMinimalDescription,
    PhaseNameWithStepNames,
)
from csorchestrator.domain.orchestrator.phase import Phase
from csorchestrator.domain.orchestrator.workflow_config import WorkflowConfig


@dataclass
class Orchestrator:
    # - create phase (e.g. setup / config / build)
    # per each phase allows to add
    #   - run custom command
    #   - get precompiled lib
    #   - add_repository
    #   - add local folder as src
    #   - run cmake workflow / individual steps (config / build / test / install)

    name: str
    version: str
    execution_matrix: ExecutionMatrixOsArchCompilerGenerator
    phases: list[Phase] = field(default_factory=list)
    wf_config: WorkflowConfig | None = None

    def add_phase(self, phase: Phase) -> "Orchestrator":
        self.phases.append(phase)
        return self

    def create_phase(self, phase_name: str) -> Phase:
        phase = Phase(phase_name)
        self.phases.append(phase)
        return phase

    def set_execution_matrix_list(self, matrix_list: list[ContextOsArchitectureCompilerGenerator]) -> "Orchestrator":
        self.execution_matrix.os_architecture_compiler_generator_list = matrix_list
        return self

    def extract_minimal_description(self) -> OrchestratorExecutorMinimalDescription:
        ret = OrchestratorExecutorMinimalDescription(name=self.name, version=self.version)
        for phase in self.phases:
            phase_desc = PhaseNameWithStepNames(phase.name)
            for step in phase.steps:
                phase_desc.step_names.append(step.name)
            ret.phases_and_steps.append(phase_desc)
            ret.matrix_description = self.execution_matrix.to_list_string_description()
        return ret
