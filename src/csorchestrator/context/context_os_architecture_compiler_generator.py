from csorchestrator.context.context_compiler_generator import ContextCompilerGenerator
from csorchestrator.context.context_os_architecture import OS, ContextOsArchitecture

cs_orchestrator_schema_version = "csv1"


def create_context_os_architecture_compiler_generator_string(
    context_os_architecture: ContextOsArchitecture,
    context_compiler_generator: ContextCompilerGenerator,
) -> str:
    """
    Creates canonical CS orchestrator ID.

    Examples:

        csv1-linux-ubuntu24.04-arm64-orin-clang-ninja
        csv1-windows11-x64-generic-msvc-vs2022
        csv1-macos14-arm64-generic-appleclang-ninjamulticonfig
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

    # windows11
    # macos14
    if context_os_architecture.os != OS.LINUX:
        os_version = context_os_architecture.os_version.lower()
        parts.append(f"{os_name}{os_version}")
    else:
        parts.append(f"{os_name}")  # skip os version for linux, contains kernel version

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

    parts.append(f"{compiler_name}")

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
