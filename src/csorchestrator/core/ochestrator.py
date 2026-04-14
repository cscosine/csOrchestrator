from dataclasses import dataclass, field
from typing import Protocol


# execution context
class LocalExecutionContext:
    pass


class GitHubActionContext:
    pass


# the output types of steps


class LocalCommand:
    pass


class GitHubActionCommand:
    pass


class TextDescription:
    pass


# the step base class
class Step(Protocol):
    def to_local_command(self, context: LocalExecutionContext) -> LocalCommand:
        """convert to a LocalCommand object"""
        ...

    def to_github_action_command(self, context: GitHubActionContext) -> GitHubActionCommand:
        """convert to a GitHubActionCommand object"""
        ...

    def to_text_description(self) -> TextDescription:
        """convert to a TextDescription object"""
        ...


# step concrete impl
class StepCustomCommand:  # impl Step(Protocol)
    pass


class StepGetPrecompiledLibFromGitHubRelase:  # impl Step(Protocol)
    pass


class StepAddRepository:  # impl Step(Protocol)
    pass


class StepAddLocalFolder:  # impl Step(Protocol)
    pass


class StepCMakeWorkflow:  # impl Step(Protocol)
    pass


# phase definition
@dataclass
class Phase:
    name: str
    steps: list[Step] = field(default_factory=list)

    def add_step(self, step: Step) -> "Phase":
        self.steps.append(step)
        return self  # <-- enables chaining addStep().addStep()


# static typing execution helpers --> not sure is needed
def stepto_local_command(step: Step, context: LocalExecutionContext) -> LocalCommand:
    return step.to_local_command(context)


def stepto_github_action_command(step: Step, context: GitHubActionContext) -> GitHubActionCommand:
    return step.to_github_action_command(context)


def stepto_text_description(step: Step) -> TextDescription:
    return step.to_text_description()


@dataclass
class Orchestrator:
    # has to support
    # - create phase (e.g. setup / config / build)
    # per each phase should allow to add
    #   - run custom command
    #   - get precompiled lib
    #   - add_repository
    #   - add local folder as src
    #   - run cmake workflow / individual steps (config / build / test / install)

    phases: list[Phase] = field(default_factory=list)

    def add_phase(self, phase: Phase) -> None:
        self.phases.append(phase)

    def create_phase(self, phase_name: str) -> Phase:
        phase = Phase(phase_name)
        self.phases.append(phase)
        return phase
