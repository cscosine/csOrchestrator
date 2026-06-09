from dataclasses import dataclass
from enum import Enum

from csorchestrator.context.context_compiler_generator import (
    Compiler,
    ContextCompilerGenerator,
    GeneratorType,
    GeneratorWithType,
)
from csorchestrator.context.context_os_architecture import (
    ARCHITECTURE_VARIANT_GENERIC,
    OS,
    UBUNTU_VERSIONS,
    WINDOWS_VERSIONS,
    Architecture,
    ContextOsArchitecture,
)
from csorchestrator.context.context_os_architecture_compiler_generator import (
    ContextOsArchitectureCompilerGenerator,
    create_context_os_architecture_compiler_generator_string,
    create_context_os_architecture_compiler_generator_string_from_components,
)

# TODO this is a glue layer between csorchestrator and cscmake
# it should not strictly belong to csorchestrator, but having it in cscmake
# at the moment is complicated: cscmake is normally cloned by project
# therefore it is not available in imports until it is cloned...
# so, for the time being, this can stay here
# once cscmake will be stable and usable via pip install, then we can move this file there


def get_supported_os_version_list(os: OS) -> list[str]:
    if os == OS.LINUX:
        return [UBUNTU_VERSIONS.UBUNTU_22_04.value, UBUNTU_VERSIONS.UBUNTU_24_04.value]
    elif os == OS.WINDOWS:
        return [WINDOWS_VERSIONS.WIN10.value]
    elif os == OS.MACOS:
        return []  # TODO add MACOS support
    else:
        return []


class BuildConfig(Enum):
    DEBUG = "debug"
    RELEASE = "release"
    PARANOID = "paranoid"
    RELWITHDEBINFO = "relWithDebInfo"
    DEBUG_RELEASE = "debug-release"
    DEBUG_RELEASE_RELWITHDEBINFO_PARANOID = "debug-release-relWithDebInfo-paranoid"


def get_supported_build_configs_for_generator_type(
    generator_type: GeneratorType,
) -> list[BuildConfig]:
    if generator_type == GeneratorType.SINGLE_CONFIG:
        return [
            BuildConfig.DEBUG,
            BuildConfig.RELEASE,
            BuildConfig.RELWITHDEBINFO,
            BuildConfig.PARANOID,
        ]
    elif generator_type == GeneratorType.MULTI_CONFIG:
        return [
            BuildConfig.DEBUG,
            BuildConfig.RELEASE,
            BuildConfig.RELWITHDEBINFO,
            BuildConfig.PARANOID,
            BuildConfig.DEBUG_RELEASE,
            BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID,
        ]
    else:
        # defensive, for invalid cases
        return []


def get_supported_generators_linux() -> list[GeneratorWithType]:
    return [
        GeneratorWithType.NINJA,
        GeneratorWithType.NINJA_MULTI,
    ]


def get_supported_generators_windows(use_ninja: bool) -> list[GeneratorWithType]:
    if use_ninja:
        return [
            GeneratorWithType.NINJA,
            GeneratorWithType.NINJA_MULTI,
        ]
    else:
        return [
            GeneratorWithType.MSVC_17_2022,
            GeneratorWithType.MSVC_18_2026,
        ]


def get_supported_compilers_linux() -> list[Compiler]:
    return [Compiler.GCC, Compiler.CLANG]


def get_supported_compilers_windows(use_ninja: bool) -> list[tuple[Compiler, str]]:
    if not use_ninja:
        return [
            (Compiler.MSVC, ContextCompilerGenerator.COMPILER_VERSION_DEFAULT),
            (Compiler.MSVC_CLANG, ContextCompilerGenerator.COMPILER_VERSION_DEFAULT),
        ]
    else:
        return [
            (Compiler.MSVC, ContextCompilerGenerator.COMPILER_VERSION_MSVC_2022_17),
            (Compiler.MSVC_CLANG, ContextCompilerGenerator.COMPILER_VERSION_MSVC_2022_17),
            (Compiler.MSVC, ContextCompilerGenerator.COMPILER_VERSION_MSVC_2026_18),
            (Compiler.MSVC_CLANG, ContextCompilerGenerator.COMPILER_VERSION_MSVC_2026_18),
        ]


def get_supported_context_os_architecture_list(
    use_ninja_for_windows: bool,
) -> list[ContextOsArchitectureCompilerGenerator]:

    retList: list[ContextOsArchitectureCompilerGenerator] = []

    ## LINUX
    for os_version in get_supported_os_version_list(OS.LINUX):
        os_arch = ContextOsArchitecture(
            os=OS.LINUX,
            os_version=os_version,
            architecture=Architecture.X64,
            architecture_variant=ARCHITECTURE_VARIANT_GENERIC,
        )
        generators = get_supported_generators_linux()
        compilers = get_supported_compilers_linux()

        for compiler in compilers:
            for generator in generators:
                ccg = ContextCompilerGenerator(
                    compiler_family=compiler,
                    compiler_version=ContextCompilerGenerator.COMPILER_VERSION_DEFAULT,
                    build_generator=generator,
                )
                retList.append(
                    ContextOsArchitectureCompilerGenerator(
                        context_os_architecture=os_arch, context_compiler_generator=ccg
                    )
                )

    ## WINDOWS
    for os_version in get_supported_os_version_list(OS.WINDOWS):
        os_arch = ContextOsArchitecture(
            os=OS.WINDOWS,
            os_version=os_version,
            architecture=Architecture.X64,
            architecture_variant=ARCHITECTURE_VARIANT_GENERIC,
        )

        generators = get_supported_generators_windows(use_ninja=use_ninja_for_windows)
        compilers_and_version = get_supported_compilers_windows(use_ninja=use_ninja_for_windows)

        for compiler, version in compilers_and_version:
            for generator in generators:
                ccg = ContextCompilerGenerator(
                    compiler_family=compiler,
                    compiler_version=version,
                    build_generator=generator,
                )
                retList.append(
                    ContextOsArchitectureCompilerGenerator(
                        context_os_architecture=os_arch, context_compiler_generator=ccg
                    )
                )
    ## MACOS
    # for os_version in get_supported_os_version_list(OS.MACOS):
    #     _ = os_version  # TODO add MACOS support

    return retList


@dataclass
class ContextOsArchitectureCompilerGeneratorConfig(ContextOsArchitectureCompilerGenerator):
    config: BuildConfig


def get_supported_context_os_architecture_config_list(
    src_list: list[ContextOsArchitectureCompilerGenerator],
) -> list[ContextOsArchitectureCompilerGeneratorConfig]:

    retList: list[ContextOsArchitectureCompilerGeneratorConfig] = []

    for src in src_list:
        configs_per_generator_type = get_supported_build_configs_for_generator_type(
            src.context_compiler_generator.build_generator.generator_type
        )
        for config in configs_per_generator_type:
            retList.append(
                ContextOsArchitectureCompilerGeneratorConfig(
                    context_os_architecture=src.context_os_architecture,
                    context_compiler_generator=src.context_compiler_generator,
                    config=config,
                )
            )

    return retList


def is_config_selected_multi_config_generator(current_config: BuildConfig, requested_config: BuildConfig) -> bool:
    # verbose but defensive, if used without type checks in place
    if (
        requested_config == BuildConfig.DEBUG
        or requested_config == BuildConfig.RELEASE
        or requested_config == BuildConfig.RELWITHDEBINFO
        or requested_config == BuildConfig.PARANOID
        or requested_config == BuildConfig.DEBUG_RELEASE
        or requested_config == BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID
    ):
        if requested_config == current_config:
            return True
        return False
    else:
        return False


def is_config_selected_single_config_generator(current_config: BuildConfig, requested_config: BuildConfig) -> bool:
    if (
        requested_config == BuildConfig.DEBUG
        or requested_config == BuildConfig.RELEASE
        or requested_config == BuildConfig.RELWITHDEBINFO
        or requested_config == BuildConfig.PARANOID
    ):
        if current_config == requested_config:
            return True
    elif requested_config == BuildConfig.DEBUG_RELEASE:
        if current_config == BuildConfig.DEBUG or current_config == BuildConfig.RELEASE:
            return True
    elif requested_config == BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID:
        if (
            current_config == BuildConfig.DEBUG
            or current_config == BuildConfig.RELEASE
            or current_config == BuildConfig.RELWITHDEBINFO
            or current_config == BuildConfig.PARANOID
        ):
            return True
    return False


def is_config_selected_for_generator(
    generator_type: GeneratorType,
    current_config: BuildConfig,
    requested_config: BuildConfig,
) -> bool:
    if generator_type == GeneratorType.SINGLE_CONFIG:
        return is_config_selected_single_config_generator(
            current_config=current_config, requested_config=requested_config
        )
    elif generator_type == GeneratorType.MULTI_CONFIG:
        return is_config_selected_multi_config_generator(
            current_config=current_config, requested_config=requested_config
        )
    else:
        return False


def workflow_name_from_description(
    description: ContextOsArchitectureCompilerGeneratorConfig,
) -> str:
    supported_build_config_string = create_context_os_architecture_compiler_generator_string(description)

    config_string = description.config.value
    workflow_name = f"workflow-{supported_build_config_string}-{config_string}"
    return workflow_name


def workflow_name_from_components(
    os: str,
    os_version: str,
    architecture: str,
    architecture_variant: str,
    compiler: str,
    compiler_version: str,
    build_generator: str,
    config_string: str,
) -> str:

    supported_build_config_string = create_context_os_architecture_compiler_generator_string_from_components(
        os, os_version, architecture, architecture_variant, compiler, compiler_version, build_generator
    )

    workflow_name = f"workflow-{supported_build_config_string}-{config_string}"
    return workflow_name


def get_all_supported_workflow_descriptions(
    selected_config: BuildConfig,
    os_arch_generator: ContextOsArchitectureCompilerGenerator,
) -> list[ContextOsArchitectureCompilerGeneratorConfig]:
    workflow_list: list[ContextOsArchitectureCompilerGeneratorConfig] = []

    for supported_build_config in get_supported_context_os_architecture_config_list([os_arch_generator]):
        if not is_config_selected_for_generator(
            supported_build_config.context_compiler_generator.build_generator.generator_type,
            supported_build_config.config,
            selected_config,
        ):
            continue
        workflow_list.append(supported_build_config)

    return workflow_list
