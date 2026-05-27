# execution context
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar

from csorchestrator.context.context_os_architecture import ContextOsArchitecture
from csorchestrator.context.context_os_architecture_compiler_generator import ContextOsArchitectureCompilerGenerator


# base class for extra information that can be provided
class ContextLocalExecutionExtra:
    pass


T = TypeVar("T", bound="ContextLocalExecutionExtra")


# create it with create_local_context to ensure is a valid path pointint to an existing (eventually created) folder
@dataclass(frozen=True)
class ContextLocalExecution:
    base_folder_path: Path
    os_architecture: ContextOsArchitecture
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

    def get_extra(self, t: type[T]) -> T | None:
        extra = self._extras.get(t)
        return extra if isinstance(extra, t) else None

    def get_context_os_architecture_compiler_generator(
        self,
    ) -> ContextOsArchitectureCompilerGenerator | None:
        return None

    def create_context_with_matrix_config(
        self,
        compiler_generator: ContextOsArchitectureCompilerGenerator,
    ) -> "ContextLocalExecutionWithMatrixConfig":
        return ContextLocalExecutionWithMatrixConfig(
            base_folder_path=self.base_folder_path,
            os_architecture=self.os_architecture,
            _extras=self._extras,  # note: do not copy, we need to share to update the original context
            _os_architecture_compiler_generator=compiler_generator,
        )


@dataclass(frozen=True)
class ContextLocalExecutionWithMatrixConfig(ContextLocalExecution):
    _os_architecture_compiler_generator: ContextOsArchitectureCompilerGenerator

    def get_context_os_architecture_compiler_generator(
        self,
    ) -> ContextOsArchitectureCompilerGenerator | None:
        return self._os_architecture_compiler_generator
