"""Step type definitions."""

from csorchestrator.step.step_cmake_command import StepCMakeWorkflow
from csorchestrator.step.step_custom_command import StepBashScriptCommand
from csorchestrator.step.step_get_precompiled_lib import StepGetPrecompiledLib
from csorchestrator.step.step_get_repository import StepGetRepositoryGitHub

__all__ = [
    "StepCMakeWorkflow",
    "StepBashScriptCommand",
    "StepGetPrecompiledLib",
    "StepGetRepositoryGitHub",
]
