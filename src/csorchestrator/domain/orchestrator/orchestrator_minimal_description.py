from dataclasses import dataclass, field


@dataclass(frozen=True)
class PhaseNameWithStepNames:
    phase_name: str
    step_names: list[str] = field(default_factory=list)


@dataclass
class OrchestratorExecutorMinimalDescription:
    name: str
    version: str
    phases_and_steps: list[PhaseNameWithStepNames] = field(
        default_factory=list
    )  # a list of phases names and list of step names
    matrix_description: list[str] = field(default_factory=list)  # a list of string describing the execution matrix
