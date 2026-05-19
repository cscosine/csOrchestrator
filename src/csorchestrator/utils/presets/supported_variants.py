from dataclasses import dataclass
from enum import Enum

from csorchestrator.context.context_compiler_generator import (
    Compiler,
    ContextCompilerGenerator,
    Generator,
)
from csorchestrator.context.context_os_architecture import OS, Architecture, ContextOsArchitecture
from csorchestrator.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string,
)


class GeneratorType(Enum):
    SINGLE_CONFIG = "singleconfig"
    MULTI_CONFIG = "multiconfig"


class BuildConfig(Enum):
    DEBUG = "debug"
    RELEASE = "release"
    PARANOID = "paranoid"
    RELWITHDEBINFO = "relWithDebInfo"
    DEBUG_RELEASE = "debug-release"
    DEBUG_RELEASE_RELWITHDEBINFO_PARANOID = "debug-release-relWithDebInfo-paranoid"


def get_supported_build_configs_for_generator_type(generator_type: GeneratorType | None) -> list[BuildConfig]:
    if generator_type is None:
        return [
            BuildConfig.DEBUG,
            BuildConfig.RELEASE,
            BuildConfig.RELWITHDEBINFO,
            BuildConfig.PARANOID,
            BuildConfig.DEBUG_RELEASE,
            BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID,
        ]
    if generator_type == GeneratorType.SINGLE_CONFIG:
        return [BuildConfig.DEBUG, BuildConfig.RELEASE, BuildConfig.RELWITHDEBINFO, BuildConfig.PARANOID]
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
        return []


@dataclass
class ContextOsArchitectureCompilerGeneratorConfig:
    context_os_architecture: ContextOsArchitecture
    context_compiler_generator: ContextCompilerGenerator
    config: BuildConfig


def get_supported_os_version_list(os: OS) -> list[str]:
    if os == OS.LINUX:
        return ["ubuntu24.04"]
    elif os == OS.WINDOWS:
        return ["v10", "v11"]
    elif os == OS.MACOS:
        return []  # TODO add macos support
    else:
        return []


def get_supported_context_os_architecture_list(
    generator_type: GeneratorType | None = None,
) -> list[ContextOsArchitectureCompilerGeneratorConfig]:

    retList: list[ContextOsArchitectureCompilerGeneratorConfig] = []

    ## LINUX
    for os_version in get_supported_os_version_list(OS.LINUX):
        linux_ubuntu2404_x64_generic = ContextOsArchitecture(
            os=OS.LINUX,
            os_version=os_version,
            architecture=Architecture.X64,
            architecture_variant=ContextOsArchitecture.ARCHITECTURE_VARIANT_GENERIC,
        )
        configs_per_generator_type = get_supported_build_configs_for_generator_type(generator_type)
        if generator_type is None:
            generators = [Generator.NINJA, Generator.NINJA_MULTI]
            configs = [configs_per_generator_type, configs_per_generator_type]
        elif generator_type == GeneratorType.SINGLE_CONFIG:
            generators = [Generator.NINJA]
            configs = [configs_per_generator_type]
        elif generator_type == GeneratorType.MULTI_CONFIG:
            generators = [Generator.NINJA_MULTI]
            configs = [configs_per_generator_type]
        else:
            generators = []
            configs = []

        for compiler in [Compiler.CLANG, Compiler.GCC]:
            for generator, config_list in zip(generators, configs, strict=True):
                ccg = ContextCompilerGenerator(compiler_family=compiler, build_generator=generator)
                for config in config_list:
                    retList.append(
                        ContextOsArchitectureCompilerGeneratorConfig(
                            context_os_architecture=linux_ubuntu2404_x64_generic,
                            context_compiler_generator=ccg,
                            config=config,
                        )
                    )

    ## WINDOWS
    for os_version in get_supported_os_version_list(OS.WINDOWS):
        windows_x64_generic = ContextOsArchitecture(
            os=OS.WINDOWS,
            os_version=os_version,
            architecture=Architecture.X64,
            architecture_variant=ContextOsArchitecture.ARCHITECTURE_VARIANT_GENERIC,
        )
        configs_per_generator_type = get_supported_build_configs_for_generator_type(generator_type)
        if generator_type is None:
            generators = [Generator.MSVC_17_2022, Generator.MSVC_18_2026]
            configs = [configs_per_generator_type, configs_per_generator_type]
        elif generator_type == GeneratorType.SINGLE_CONFIG:
            generators = []
            configs = []
        elif generator_type == GeneratorType.MULTI_CONFIG:
            generators = [Generator.MSVC_17_2022, Generator.MSVC_18_2026]
            configs = [configs_per_generator_type, configs_per_generator_type]
        else:
            generators = []
            configs = []

        for compiler in [Compiler.MSVC, Compiler.MSVC_CLANG]:
            for generator, config_list in zip(generators, configs, strict=True):
                ccg = ContextCompilerGenerator(compiler_family=compiler, build_generator=generator)
                for config in config_list:
                    retList.append(
                        ContextOsArchitectureCompilerGeneratorConfig(
                            context_os_architecture=windows_x64_generic, context_compiler_generator=ccg, config=config
                        )
                    )
    ## MACOS
    for os_version in get_supported_os_version_list(OS.MACOS):
        _ = os_version  # TODO add macos support

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


def workflow_name_from_description(description: ContextOsArchitectureCompilerGeneratorConfig) -> str:
    supported_build_config_string = create_context_os_architecture_compiler_generator_string(
        description.context_os_architecture, description.context_compiler_generator
    )
    config_string = description.config.value
    workflow_name = f"workflow-{supported_build_config_string}-{config_string}"
    return workflow_name


def get_all_supported_workflow_descriptions(
    selected_config: BuildConfig,
) -> list[ContextOsArchitectureCompilerGeneratorConfig]:
    workflow_list: list[ContextOsArchitectureCompilerGeneratorConfig] = []
    for supported_build_config in get_supported_context_os_architecture_list(GeneratorType.SINGLE_CONFIG):
        if not is_config_selected_single_config_generator(supported_build_config.config, selected_config):
            continue
        workflow_list.append(supported_build_config)

    for supported_build_config in get_supported_context_os_architecture_list(GeneratorType.MULTI_CONFIG):
        if not is_config_selected_multi_config_generator(supported_build_config.config, selected_config):
            continue
        workflow_list.append(supported_build_config)

    return workflow_list
