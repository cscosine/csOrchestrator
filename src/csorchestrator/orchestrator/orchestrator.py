from dataclasses import dataclass, field
from typing import TypeAlias

from csorchestrator.ci.github.github_workflow_config import CreateGitHubWorkflowConfig, GitHubWorkflow, create_github_wf
from csorchestrator.context.context_os_architecture_compiler_generator import (
    ContextOsArchitectureCompilerGenerator,
    ExecutionMatrixOsArchCompilerGenerator,
)
from csorchestrator.context.orchestrator_minimal_description import (
    OrchestratorExecutorMinimalDescription,
    PhaseNameWithStepNames,
)
from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.utils.presets.supported_variants import get_supported_context_os_architecture_list


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


def create_orchestrator_factory(name: str, version: str, execution_matrix_name: str) -> Orchestrator:
    return Orchestrator(
        name=name,
        version=version,
        execution_matrix=ExecutionMatrixOsArchCompilerGenerator(execution_matrix_name),
    )


def create_orchestrator_factory_all_supported_cases(
    name: str,
    version: str,
    execution_matrix_name: str,
    use_ninja_for_windows: bool = False,
    use_ninja: bool = True,
    use_ninjamulti: bool = True,
) -> Orchestrator:
    o = Orchestrator(
        name=name,
        version=version,
        execution_matrix=ExecutionMatrixOsArchCompilerGenerator(execution_matrix_name),
    )
    o.set_execution_matrix_list(
        get_supported_context_os_architecture_list(
            use_ninja_for_windows=use_ninja_for_windows,
            use_ninja=use_ninja,
            use_ninjamulti=use_ninjamulti,
        )
    )
    return o


OptionalOrchestratorWithReport: TypeAlias = OptionalResultWithReport[Orchestrator]
