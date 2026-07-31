from abc import ABC
from dataclasses import dataclass, field

from csorchestrator.domain.orchestrator.orchestrator_minimal_description import (
    OrchestratorExecutorMinimalDescription,
    PhaseNameWithStepNames,
)
from csorchestrator.domain.orchestrator.phase import Phase
from csorchestrator.domain.orchestrator.workflow_config import WorkflowConfig


# TODO support capabilities here to be more generic?
@dataclass
class MatrixExecutionBase(ABC):
    name: str

    def to_list_string_description(self) -> list[str]:
        return []


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
    execution_matrix: MatrixExecutionBase
    phases: list[Phase] = field(default_factory=list)
    wf_config: WorkflowConfig | None = None

    def name_version_to_string(self, separator: str = "-") -> str:
        return f"{self.name}{separator}{self.version}"

    def add_phase(self, phase: Phase) -> "Orchestrator":
        self.phases.append(phase)
        return self

    def create_phase(self, phase_name: str) -> Phase:
        phase = Phase(phase_name)
        self.phases.append(phase)
        return phase

    def extract_minimal_description(self) -> OrchestratorExecutorMinimalDescription:
        ret = OrchestratorExecutorMinimalDescription(name=self.name, version=self.version)
        for phase in self.phases:
            phase_desc = PhaseNameWithStepNames(phase.name)
            for step in phase.steps:
                phase_desc.step_names.append(step.name)
            ret.phases_and_steps.append(phase_desc)
            ret.matrix_description = self.execution_matrix.to_list_string_description()
        return ret
