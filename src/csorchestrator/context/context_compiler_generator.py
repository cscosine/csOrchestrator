import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from csorchestrator.core.expected import Expected


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


Runner = Callable[[list[str]], str | None]


def detect_compiler_version_run(cmd: list[str]) -> str | None:
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        if p.returncode != 0:
            return None
        return p.stdout
    except Exception:
        return None


def detect_compiler_version(compiler: Compiler, runner: Runner = detect_compiler_version_run) -> Expected[str, str]:
    """
    Returns normalized MAJOR compiler version.

    Examples:
        GCC 13.2.0      -> 13
        Clang 18.1.3    -> 18
        Apple Clang 16  -> 16
        MSVC 19.38      -> 143
    """

    # -------------------------
    # GCC
    # -------------------------
    if compiler == Compiler.GCC:
        out = runner(["g++", "--version"]) or ""

        m = re.search(r"(\d+)(\.\d+)+", out)

        if not m:
            return Expected(error="Cannot detect GCC version")

        return Expected(value=m.group(1))

    # -------------------------
    # CLANG (upstream)
    # -------------------------
    if compiler == Compiler.CLANG:
        out = runner(["clang++", "--version"]) or ""

        m = re.search(r"clang version (\d+)(\.\d+)*", out)

        if not m:
            return Expected(error="Cannot detect Clang version")

        return Expected(value=m.group(1))

    # -------------------------
    # APPLE CLANG
    # -------------------------
    if compiler == Compiler.APPLE_CLANG:
        out = runner(["clang++", "--version"]) or ""

        m = re.search(r"Apple clang version (\d+)(\.\d+)*", out)

        if not m:
            return Expected(error="Cannot detect Apple Clang version")

        return Expected(value=m.group(1))

    # -------------------------
    # MSVC
    # -------------------------
    if compiler == Compiler.MSVC:
        out = runner(["cl"]) or ""

        m = re.search(r"Version\s+(\d+)\.(\d+)", out)

        if not m:
            return Expected(error="Cannot detect MSVC version")

        major = int(m.group(1))
        minor = int(m.group(2))

        # 19.3x => v143
        if major == 19 and minor >= 30:
            return Expected(value="143")

        # 19.2x => v142
        if major == 19 and minor >= 20:
            return Expected(value="142")

        return Expected(value=f"{major}{minor}")

    return Expected(error=f"Unsupported compiler: {compiler}")
