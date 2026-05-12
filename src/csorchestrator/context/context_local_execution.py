# execution context
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from csorchestrator.context.context_compiler_generator import ContextCompilerGenerator
from csorchestrator.context.context_os_architecture import ContextOsArchitecture
from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.utils.file_system.directory import ensure_directory_exists_or_create_and_is_usable


# create it with create_local_context to ensure is a valid path pointint to an existing (eventually created) folder
@dataclass(frozen=True)
class ContextLocalExecution:
    base_folder_path: Path


OptionalContextLocalExecutionWithReport: TypeAlias = OptionalResultWithReport[ContextLocalExecution]


def create_context_local_execution(path: str) -> OptionalContextLocalExecutionWithReport:
    pr = ensure_directory_exists_or_create_and_is_usable(path)

    if pr.result is not None:
        return OptionalContextLocalExecutionWithReport.createResultAndReport(
            ContextLocalExecution(base_folder_path=pr.result), pr.report
        )
    else:
        return OptionalContextLocalExecutionWithReport.createReport(pr.report)


cs_orchestrator_schema_version = "csv1"


def create_context_id(
    context_os_architecture: ContextOsArchitecture,
    context_compiler_generator: ContextCompilerGenerator,
) -> str:
    """
    Creates canonical CS orchestrator ID.

    Examples:

        csv1-linux-ubuntu24.04-arm64-orin-clang18-ninja
        csv1-windows11-x64-generic-msvc143-vs17
        csv1-macos14-arm64-generic-appleclang16-ninjamulticonfig
    """

    parts: list[str] = []

    # =====================================================
    # SCHEMA
    # =====================================================

    parts.append(cs_orchestrator_schema_version.lower())

    # =====================================================
    # OS
    # =====================================================

    os_name = context_os_architecture.os.value.lower()

    os_version = context_os_architecture.os_version.lower()

    # windows11
    # macos14
    parts.append(f"{os_name}{os_version}")

    # =====================================================
    # DISTRO
    # =====================================================

    if context_os_architecture.os_distro:
        distro = context_os_architecture.os_distro.lower()

        # ubuntu24.04
        parts.append(f"{distro}")

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

    compiler_version = context_compiler_generator.compiler_version.lower()

    # clang18
    # gcc13
    # msvc143
    parts.append(f"{compiler_name}{compiler_version}")

    # =====================================================
    # GENERATOR
    # =====================================================

    generator_name = context_compiler_generator.build_generator.value.lower()

    generator_version = context_compiler_generator.build_generator_version.lower()

    parts.append(f"{generator_name}{generator_version}")

    # =====================================================
    # FINAL
    # =====================================================

    return "-".join(parts)
