from dataclasses import dataclass
from enum import Enum


class Compiler(Enum):
    MSVC = "msvc"
    CLANG = "clang"
    GCC = "gcc"
    APPLE_CLANG = "appleclang"


class Generator(Enum):
    NINJA = "ninja"
    NINJA_MULTI = "ninjamulticonfig"
    VS_17_2022 = "vs2022"
    VS_18_2026 = "vs2026"


@dataclass(frozen=True)
class ContextCompilerGenerator:
    compiler_family: Compiler

    build_generator: Generator
