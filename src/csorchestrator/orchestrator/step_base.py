from abc import ABC, abstractmethod
from dataclasses import dataclass

from csorchestrator.commands.command_github_action import CommandGithubAction
from csorchestrator.commands.command_local import CommandLocal
from csorchestrator.commands.command_text_description import CommandTextDescription
from csorchestrator.context.context_github_execution import ContextGithubExecution
from csorchestrator.context.context_local_execution import ContextLocalExecution


# the step base class
@dataclass
class StepBase(ABC):
    name: str
    description: str

    @abstractmethod
    def to_local_command(self, context: ContextLocalExecution) -> CommandLocal:
        """convert to a LocalCommand object"""
        ...

    @abstractmethod
    def to_github_action_command(self, context: ContextGithubExecution) -> CommandGithubAction:
        """convert to a GithubActionCommand object"""
        ...

    @abstractmethod
    def to_text_description(self) -> CommandTextDescription:
        """convert to a TextDescription object"""
        ...
