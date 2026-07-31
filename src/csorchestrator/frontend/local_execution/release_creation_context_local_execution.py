from dataclasses import dataclass
from pathlib import Path

from csorchestrator.domain.context.context_os_architecture import ContextOsArchitecture
from csorchestrator.domain.context.context_os_architecture_compiler_generator import (
    ContextOsArchitectureCompilerGenerator,
)


@dataclass(frozen=True)
class ReleaseCreationContextLocalExecution:
    os_architecture_compiler_generator_list: list[ContextOsArchitectureCompilerGenerator]
    name_and_version_string: str
    os_architecture: ContextOsArchitecture
    base_path: Path
