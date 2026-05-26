"""Execution contexts."""

from csorchestrator.context.context_github_execution import ContextGithubExecution
from csorchestrator.context.context_local_execution import ContextLocalExecution

__all__ = [
    "ContextGithubExecution",
    "ContextLocalExecution",
]
