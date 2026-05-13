from csorchestrator.context.context_compiler_generator import Compiler, ContextCompilerGenerator, Generator
from csorchestrator.context.context_os_architecture import OS, Architecture, ContextOsArchitecture
from csorchestrator.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string,
)


def test_basic_linux_ninja_clang():
    context_os = ContextOsArchitecture(
        os=OS.LINUX,
        os_version="6.8",
        os_distro="ubuntu24.04",
        architecture=Architecture.ARM64,
        architecture_variant="orin",
    )

    context_compiler = ContextCompilerGenerator(
        compiler_family=Compiler.CLANG,
        build_generator=Generator.NINJA,
        build_generator_version="1.0",
    )

    result = create_context_os_architecture_compiler_generator_string(context_os, context_compiler)

    assert result == "csv1-linux-ubuntu24.04-arm64-orin-clang-ninja1.0"


def test_windows_msvc_vs_generator():
    context_os = ContextOsArchitecture(
        os=OS.WINDOWS,
        os_version="11",
        os_distro="",
        architecture=Architecture.X64,
        architecture_variant="generic",
    )

    context_compiler = ContextCompilerGenerator(
        compiler_family=Compiler.MSVC,
        build_generator=Generator.VS,
        build_generator_version="2022",
    )

    result = create_context_os_architecture_compiler_generator_string(context_os, context_compiler)

    assert result == "csv1-windows11-x64-generic-msvc-vs2022"


def test_macos_appleclang_ninja_multiconfig():
    context_os = ContextOsArchitecture(
        os=OS.MACOS,
        os_version="14",
        os_distro="",
        architecture=Architecture.ARM64,
        architecture_variant="generic",
    )

    context_compiler = ContextCompilerGenerator(
        compiler_family=Compiler.APPLE_CLANG,
        build_generator=Generator.NINJA_MULTI,
        build_generator_version="3",
    )

    result = create_context_os_architecture_compiler_generator_string(context_os, context_compiler)

    assert result == "csv1-macos14-arm64-generic-appleclang-ninjamulticonfig3"


def test_distro_is_included_only_when_present():
    context_os = ContextOsArchitecture(
        os=OS.LINUX,
        os_version="6.6",
        os_distro="ubuntu24.04",
        architecture=Architecture.X64,
        architecture_variant="generic",
    )

    context_compiler = ContextCompilerGenerator(
        compiler_family=Compiler.GCC,
        build_generator=Generator.NINJA,
        build_generator_version="2.0",
    )

    result = create_context_os_architecture_compiler_generator_string(context_os, context_compiler)

    # distro must appear in output
    assert "ubuntu24.04" in result
    assert result.startswith("csv1-linux-ubuntu24.04-x64-generic-gcc-ninja2.0")


def test_empty_distro_is_skipped():
    context_os = ContextOsArchitecture(
        os=OS.WINDOWS,
        os_version="11",
        os_distro="",
        architecture=Architecture.X64,
        architecture_variant="generic",
    )

    context_compiler = ContextCompilerGenerator(
        compiler_family=Compiler.MSVC,
        build_generator=Generator.VS,
        build_generator_version="2026",
    )

    result = create_context_os_architecture_compiler_generator_string(context_os, context_compiler)

    # ensure no double hyphen from empty distro
    assert "--" not in result
    assert result.startswith("csv1-windows11-x64-generic-msvc-vs2026")


def test_lowercasing_behavior():
    context_os = ContextOsArchitecture(
        os=OS.LINUX,
        os_version="UbUnTu24.04",
        os_distro="UbUnTu",
        architecture=Architecture.ARM64,
        architecture_variant="OrIn",
    )

    context_compiler = ContextCompilerGenerator(
        compiler_family=Compiler.CLANG,
        build_generator=Generator.NINJA,
        build_generator_version="X.Y",
    )

    result = create_context_os_architecture_compiler_generator_string(context_os, context_compiler)

    assert result == "csv1-linux-ubuntu-arm64-orin-clang-ninjax.y"


def test_all_generators_supported():
    base_os = ContextOsArchitecture(
        os=OS.LINUX,
        os_version="5.0",
        os_distro="ubuntu",
        architecture=Architecture.X64,
        architecture_variant="generic",
    )

    for gen, expected in [
        (Generator.NINJA, "ninja"),
        (Generator.NINJA_MULTI, "ninjamulticonfig"),
        (Generator.VS, "vs"),
    ]:
        context_compiler = ContextCompilerGenerator(
            compiler_family=Compiler.GCC,
            build_generator=gen,
            build_generator_version="1",
        )

        result = create_context_os_architecture_compiler_generator_string(base_os, context_compiler)

        assert expected in result
