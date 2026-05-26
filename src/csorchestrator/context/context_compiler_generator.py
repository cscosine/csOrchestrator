from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class Compiler(Enum):
    MSVC = "msvc"
    MSVC_CLANG = "msvcclang"
    CLANG = "clang"
    GCC = "gcc"
    APPLE_CLANG = "appleclang"


class Generator(Enum):
    NINJA = "ninja"
    NINJA_MULTI = "ninjamulticonfig"
    MSVC_17_2022 = "msvc2022"
    MSVC_18_2026 = "msvc2026"


class GeneratorType(Enum):
    SINGLE_CONFIG = "singleconfig"
    MULTI_CONFIG = "multiconfig"


@dataclass(frozen=True)
class GeneratorWithType:
    generator: Generator
    generator_type: GeneratorType

    # class vars (declared for typing only)
    NINJA: ClassVar["GeneratorWithType"]
    NINJA_MULTI: ClassVar["GeneratorWithType"]
    MSVC_17_2022: ClassVar["GeneratorWithType"]
    MSVC_18_2026: ClassVar["GeneratorWithType"]


# define them AFTER the class exists
GeneratorWithType.NINJA = GeneratorWithType(
    Generator.NINJA,
    GeneratorType.SINGLE_CONFIG,
)

GeneratorWithType.NINJA_MULTI = GeneratorWithType(
    Generator.NINJA_MULTI,
    GeneratorType.MULTI_CONFIG,
)

GeneratorWithType.MSVC_17_2022 = GeneratorWithType(
    Generator.MSVC_17_2022,
    GeneratorType.MULTI_CONFIG,
)

GeneratorWithType.MSVC_18_2026 = GeneratorWithType(
    Generator.MSVC_18_2026,
    GeneratorType.MULTI_CONFIG,
)


@dataclass(frozen=True)
class ContextCompilerGenerator:
    compiler_family: Compiler
    compiler_version: str  # string, use "default" for os/generator default compiler

    build_generator: GeneratorWithType

    COMPILER_VERSION_DEFAULT: str = "default"
