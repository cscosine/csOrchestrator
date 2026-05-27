from dataclasses import dataclass, field

from csorchestrator.context.context_compiler_generator import ContextCompilerGenerator
from csorchestrator.context.context_os_architecture import ContextOsArchitecture

cs_orchestrator_schema_version = "csv1"


@dataclass
class ContextOsArchitectureCompilerGenerator:
    context_os_architecture: ContextOsArchitecture
    context_compiler_generator: ContextCompilerGenerator


@dataclass
class ExecutionMatrixOsArchCompilerGenerator:
    os_architecture_compiler_generator_list: list[ContextOsArchitectureCompilerGenerator] = field(default_factory=list)

    def to_list_string_description(self) -> list[str]:
        ret: list[str] = []
        for c in self.os_architecture_compiler_generator_list:
            ret.append(create_context_os_architecture_compiler_generator_string(c))
        return ret


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

    parts: list[str] = []

    context_os_architecture = context_os_architecture_generator.context_os_architecture
    context_compiler_generator = context_os_architecture_generator.context_compiler_generator

    # =====================================================
    # SCHEMA
    # =====================================================

    parts.append(cs_orchestrator_schema_version.lower())

    # =====================================================
    # OS
    # =====================================================

    os_name = context_os_architecture.os.value.lower()

    # windows-11
    # macos-14
    # linux-ubuntu22.04
    os_version = context_os_architecture.os_version.lower()
    parts.append(f"{os_name}-{os_version}")

    # =====================================================
    # ARCHITECTURE
    # =====================================================

    parts.append(context_os_architecture.architecture.value.lower())

    # =====================================================
    # ARCH VARIANT
    # =====================================================

    parts.append(context_os_architecture.architecture_variant.lower())

    # =====================================================
    # COMPILER
    # =====================================================

    compiler_name = context_compiler_generator.compiler_family.value.lower()

    parts.append(f"{compiler_name}")

    compiler_version = context_compiler_generator.compiler_version.lower()

    parts.append(f"{compiler_version}")

    # =====================================================
    # GENERATOR
    # =====================================================

    generator = context_compiler_generator.build_generator.generator.value.lower()

    parts.append(f"{generator}")

    # =====================================================
    # FINAL
    # =====================================================

    return "-".join(parts)
