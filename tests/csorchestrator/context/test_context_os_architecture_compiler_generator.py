from csorchestrator.context.context_compiler_generator import Compiler, ContextCompilerGenerator, Generator
from csorchestrator.context.context_os_architecture import OS, Architecture, ContextOsArchitecture
from csorchestrator.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string,
)


def test_basic_linux_ninja_clang():
    context_os = ContextOsArchitecture(
        os=OS.LINUX,
        os_version="ubuntu24.04",
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
        os_version="v11",
        architecture=Architecture.X64,
        architecture_variant="generic",
    )

    context_compiler = ContextCompilerGenerator(
        compiler_family=Compiler.MSVC,
        build_generator=Generator.VS,
        build_generator_version="2022",
    )

    result = create_context_os_architecture_compiler_generator_string(context_os, context_compiler)

    assert result == "csv1-windows-v11-x64-generic-msvc-vs2022"


def test_macos_appleclang_ninja_multiconfig():
    context_os = ContextOsArchitecture(
        os=OS.MACOS,
        os_version="v14",
        architecture=Architecture.ARM64,
        architecture_variant="generic",
    )

    context_compiler = ContextCompilerGenerator(
        compiler_family=Compiler.APPLE_CLANG,
        build_generator=Generator.NINJA_MULTI,
        build_generator_version="3",
    )

    result = create_context_os_architecture_compiler_generator_string(context_os, context_compiler)

    assert result == "csv1-macos-v14-arm64-generic-appleclang-ninjamulticonfig3"


def test_lowercasing_behavior():
    context_os = ContextOsArchitecture(
        os=OS.LINUX,
        os_version="UbUnTu24.04",
        architecture=Architecture.ARM64,
        architecture_variant="OrIn",
    )

    context_compiler = ContextCompilerGenerator(
        compiler_family=Compiler.CLANG,
        build_generator=Generator.NINJA,
        build_generator_version="X.Y",
    )

    result = create_context_os_architecture_compiler_generator_string(context_os, context_compiler)

    assert result == "csv1-linux-ubuntu24.04-arm64-orin-clang-ninjax.y"


def test_all_generators_supported():
    base_os = ContextOsArchitecture(
        os=OS.LINUX,
        os_version="5.0",
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
