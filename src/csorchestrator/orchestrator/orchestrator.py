from dataclasses import dataclass, field
from typing import TypeAlias

from csorchestrator.ci.github.github_workflow_config import CreateGitHubWorkflowConfig, GitHubWorkflow, create_github_wf
from csorchestrator.context.context_os_architecture_compiler_generator import ExecutionMatrixOsArchCompilerGenerator
from csorchestrator.context.orchestrator_minimal_description import (
    OrchestratorExecutorMinimalDescription,
    PhaseNameWithStepNames,
)
from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.orchestrator.phase import Phase


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
    version: str = "0.0.0"
    phases: list[Phase] = field(default_factory=list)
    _execution_matrix: ExecutionMatrixOsArchCompilerGenerator | None = None
    default_github_wf: GitHubWorkflow | None = None

    def create_default_github_workflow(self, config: CreateGitHubWorkflowConfig) -> "Orchestrator":
        self.default_github_wf = create_github_wf(self.name, config=config)
        return self

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
        ret = OrchestratorExecutorMinimalDescription(name=self.name, version=self.version)
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
