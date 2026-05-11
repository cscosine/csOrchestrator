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
    VS = (
        "vs"  # generator visual studio sln, to be decorated with build_generator_version 17 for vs 2022, 18 for vs 2026
    )


@dataclass(frozen=True)
class ContextCompilerGenerator:
    compiler_family: Compiler
    compiler_version: str

    build_generator: Generator
    build_generator_version: str


# do not forget to add     cs_orchestrator_schema_version: str e.g. "csv1" at beginning of the id string
