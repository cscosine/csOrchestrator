from dataclasses import dataclass
from enum import Enum


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


@dataclass(frozen=True)
class ContextCompilerGenerator:
    compiler_family: Compiler

    build_generator: Generator
