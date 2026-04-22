from dataclasses import dataclass


# the step base class
@dataclass
class StepBase:
    name: str
    description: str
