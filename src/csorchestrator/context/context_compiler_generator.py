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
    VS = "vs"  # generator visual studio sln, to be decorated with 2022, 2026


@dataclass(frozen=True)
class ContextCompilerGenerator:
    compiler_family: Compiler

    build_generator: Generator
    build_generator_version: str
