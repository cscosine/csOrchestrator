from dataclasses import dataclass, field

from .step import Step


# phase definition
@dataclass
class Phase:
    name: str
    steps: list[Step] = field(default_factory=list)

    def add_step(self, step: Step) -> "Phase":
        self.steps.append(step)
        return self  # <-- enables chaining addStep().addStep()
