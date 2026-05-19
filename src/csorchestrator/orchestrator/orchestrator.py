from dataclasses import dataclass, field
from typing import TypeAlias

from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.orchestrator.phase import Phase


@dataclass(frozen=True)
class PhaseNameWithStepNames:
    phase_name: str
    step_names: list[str] = field(default_factory=list)


OrchestratorExecutorMinimalDescription = list[PhaseNameWithStepNames]  # a list of phases names and list of step names


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

    def add_phase(self, phase: Phase) -> "Orchestrator":
        self.phases.append(phase)
        return self

    def create_phase(self, phase_name: str) -> Phase:
        phase = Phase(phase_name)
        self.phases.append(phase)
        return phase

    def extract_minimal_description(self) -> OrchestratorExecutorMinimalDescription:
        ret: OrchestratorExecutorMinimalDescription = []
        for phase in self.phases:
            phase_desc = PhaseNameWithStepNames(phase.name)
            for step in phase.steps:
                phase_desc.step_names.append(step.name)
            ret.append(phase_desc)
        return ret


OptionalOrchestratorWithReport: TypeAlias = OptionalResultWithReport[Orchestrator]
