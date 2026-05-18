"""Step type definitions."""

from csorchestrator.step.step_add_local_folder import StepAddLocalFolder
from csorchestrator.step.step_cmake_command import StepCMakeWorkflow
from csorchestrator.step.step_custom_command import StepCustomCommand
from csorchestrator.step.step_echo_message import StepEchoMessage
from csorchestrator.step.step_get_precompiled_lib import StepGetPrecompiledLib
from csorchestrator.step.step_get_repository import StepGetRepository

__all__ = [
    "StepAddLocalFolder",
    "StepCMakeWorkflow",
    "StepCustomCommand",
    "StepEchoMessage",
    "StepGetPrecompiledLib",
    "StepGetRepository",
]
