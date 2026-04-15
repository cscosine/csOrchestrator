from dataclasses import dataclass

from .command_github_action import CommandGithubAction
from .command_local import CommandLocal
from .command_text_description import CommandTextDescription
from .context_github_execution import ContextGithubExecution
from .context_local_execution import ContextLocalExecution
from .step import Step


@dataclass
class StepEchoMessage(Step):  # impl Step
    message: str

    def to_local_command(self, context: ContextLocalExecution) -> CommandLocal:
        """convert to a LocalCommand object"""
        return CommandLocal()  # TODO

    def to_github_action_command(self, context: ContextGithubExecution) -> CommandGithubAction:
        """convert to a GithubActionCommand object"""
        return CommandGithubAction()  # TODO

    def to_text_description(self) -> CommandTextDescription:
        return CommandTextDescription(self.name, self.description, self.message)
