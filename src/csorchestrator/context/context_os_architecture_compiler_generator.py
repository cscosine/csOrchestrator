from dataclasses import dataclass, field
from typing import TypeVar

from csorchestrator.context.context_compiler_generator import ContextCompilerGenerator
from csorchestrator.context.context_os_architecture import ContextOsArchitecture

cs_orchestrator_schema_version = "csv1"


@dataclass
class ContextOsArchitectureCompilerGenerator:
    context_os_architecture: ContextOsArchitecture
    context_compiler_generator: ContextCompilerGenerator


# base class for extra information that can be provided to matrix execution
class MatrixExecutionExtra:
    pass


T = TypeVar("T", bound="MatrixExecutionExtra")


class MatrixSkipExecutionOnNonMatchingContext(MatrixExecutionExtra):
    pass


@dataclass
class ExecutionMatrixOsArchCompilerGenerator:
    name: str
    os_architecture_compiler_generator_list: list[ContextOsArchitectureCompilerGenerator] = field(default_factory=list)
    _extras: dict[type, MatrixExecutionExtra] = field(
        default_factory=dict,
        kw_only=True,
    )

    def add_extra(
        self,
        extra: MatrixExecutionExtra,
    ) -> "ExecutionMatrixOsArchCompilerGenerator":
        key = type(extra)
        self._extras[key] = extra
        return self

    def get_extra(self, t: type[T]) -> T | None:
        extra = self._extras.get(t)
        return extra if isinstance(extra, t) else None

    def remove_extra(
        self,
        key: type[T],
    ) -> "ExecutionMatrixOsArchCompilerGenerator":
        self._extras.pop(key, None)  # no exception if not exists
        return self

    def to_list_string_description(self) -> list[str]:
        ret: list[str] = []
        for c in self.os_architecture_compiler_generator_list:
            ret.append(create_context_os_architecture_compiler_generator_string(c))
        return ret


def create_context_os_architecture_compiler_generator_string_from_components(
    os: str,
    os_version: str,
    architecture: str,
    architecture_variant: str,
    compiler: str,
    compiler_version: str,
    build_generator: str,
) -> str:
    parts: list[str] = []
    parts.append(cs_orchestrator_schema_version.lower())
    parts.append(os.lower())
    parts.append(os_version.lower())
    parts.append(architecture.lower())
    parts.append(architecture_variant.lower())
    parts.append(compiler.lower())
    parts.append(compiler_version.lower())
    parts.append(build_generator.lower())
    return "-".join(parts)


def create_context_os_architecture_compiler_generator_string(
    context_os_architecture_generator: ContextOsArchitectureCompilerGenerator,
) -> str:
    """
    Creates canonical CS orchestrator ID.

    Examples:

        csv1-linux-ubuntu24.04-arm64-orin-clang-ninja
        csv1-windows-11-x64-generic-msvc-msvc2022
        csv1-macos-14-arm64-generic-appleclang-ninjamulticonfig
    """

    context_os_architecture = context_os_architecture_generator.context_os_architecture
    context_compiler_generator = context_os_architecture_generator.context_compiler_generator

    return create_context_os_architecture_compiler_generator_string_from_components(
        context_os_architecture.os.value.lower(),
        context_os_architecture.os_version.lower(),
        context_os_architecture.architecture.value.lower(),
        context_os_architecture.architecture_variant.lower(),
        context_compiler_generator.compiler_family.value.lower(),
        context_compiler_generator.compiler_version.lower(),
        context_compiler_generator.build_generator.generator.value.lower(),
    )
