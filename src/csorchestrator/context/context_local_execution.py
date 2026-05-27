# execution context
from dataclasses import dataclass
from pathlib import Path

from csorchestrator.context.context_os_architecture import ContextOsArchitecture
from csorchestrator.context.context_os_architecture_compiler_generator import ContextOsArchitectureCompilerGenerator


# create it with create_local_context to ensure is a valid path pointint to an existing (eventually created) folder
@dataclass(frozen=True)
class ContextLocalExecution:
    base_folder_path: Path
    os_architecture: ContextOsArchitecture

    def get_context_os_architecture_compiler_generator(
        self,
    ) -> ContextOsArchitectureCompilerGenerator | None:
        return None


@dataclass(frozen=True)
class ContextLocalExecutionWithMatrixConfig(ContextLocalExecution):
    matrix_config: ContextOsArchitectureCompilerGenerator

    def get_context_os_architecture_compiler_generator(
        self,
    ) -> ContextOsArchitectureCompilerGenerator | None:
        return self.matrix_config
