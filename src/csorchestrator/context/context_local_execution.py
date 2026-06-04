# execution context
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar

from csorchestrator.context.context_compiler_generator import ContextCompilerGenerator
from csorchestrator.context.context_os_architecture import ContextOsArchitecture
from csorchestrator.context.context_os_architecture_compiler_generator import ContextOsArchitectureCompilerGenerator
from csorchestrator.context.orchestrator_minimal_description import OrchestratorExecutorMinimalDescription


# base class for extra information that can be provided
class ContextLocalExecutionExtra:
    pass


T = TypeVar("T", bound="ContextLocalExecutionExtra")


# create it with create_local_context to ensure is a valid path pointint to an existing (eventually created) folder
@dataclass(frozen=True)
class ContextLocalExecution:
    base_folder_path: Path
    os_architecture: ContextOsArchitecture
    active_compiler_generator: ContextCompilerGenerator
    orchestrator_desc: OrchestratorExecutorMinimalDescription

    def get_active_os_architecture_compiler_generator(self) -> ContextOsArchitectureCompilerGenerator:
        return ContextOsArchitectureCompilerGenerator(self.os_architecture, self.active_compiler_generator)

    _extras: dict[type, ContextLocalExecutionExtra] = field(
        default_factory=dict,
        kw_only=True,
    )

    def add_extra(
        self,
        extra: ContextLocalExecutionExtra,
    ) -> "ContextLocalExecution":
        key = type(extra)
        self._extras[key] = extra
        return self

    def remove_extra(
        self,
        key: type[T],
    ) -> "ContextLocalExecution":
        self._extras.pop(key, None)  # no exception if not exists
        return self

    def get_extra(self, t: type[T]) -> T | None:
        extra = self._extras.get(t)
        return extra if isinstance(extra, t) else None
