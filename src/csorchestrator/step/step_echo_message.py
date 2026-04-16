from dataclasses import dataclass

from csorchestrator.commands.command_github_action import CommandGithubAction
from csorchestrator.commands.command_local import CommandLocal
from csorchestrator.commands.command_text_description import CommandTextDescription
from csorchestrator.context.context_github_execution import ContextGithubExecution
from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.orchestrator.step_base import StepBase


@dataclass
class StepEchoMessage(StepBase):  # impl StepBase
    message: str

    def to_local_command(self, context: ContextLocalExecution) -> CommandLocal:
        """convert to a LocalCommand object"""
        return CommandLocal()  # TODO

    def to_github_action_command(self, context: ContextGithubExecution) -> CommandGithubAction:
        """convert to a GithubActionCommand object"""
        return CommandGithubAction()  # TODO

    def to_text_description(self) -> CommandTextDescription:
        return CommandTextDescription(self.name, self.description, self.message)
