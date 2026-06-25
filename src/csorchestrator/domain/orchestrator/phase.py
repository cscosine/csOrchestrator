from dataclasses import dataclass, field

from csorchestrator.domain.orchestrator.step_base import StepBase


# phase definition
@dataclass
class Phase:
    name: str
    steps: list[StepBase] = field(default_factory=list)

    def add_step(self, step: StepBase) -> "Phase":
        self.steps.append(step)
        return self  # <-- enables chaining addStep().addStep()
