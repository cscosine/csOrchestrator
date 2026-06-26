import platform
from unittest.mock import Mock, patch

import pytest

from csorchestrator._archive.compilers.compiler_generator import (
    detect_compiler_version,
    detect_compiler_version_run,
)
from csorchestrator.domain.context.context_compiler_generator import Compiler
from csorchestrator.domain.context.context_os_architecture import OS, OS_PLATFORM_MACOS

# =========================================================
# WINDOWS TESTS
# =========================================================


@pytest.mark.skipif(platform.system().lower() != OS.WINDOWS.value, reason=OS.WINDOWS.value + "-only test")
@pytest.mark.requires("cl")  # if run-all this will be forced to run, all tests will run in the continuous integration.
# on local execution, without run-all, will be allowed to skip if the compiler is not installed
def test_windows_msvc_real():

    result = detect_compiler_version(Compiler.MSVC)

    assert result.error is None
    assert result.value is not None
    assert result.value.isdigit()


@pytest.mark.skipif(platform.system().lower() != OS.WINDOWS.value, reason=OS.WINDOWS.value + "-only test")
@pytest.mark.requires(
    "clang++"
)  # if run-all this will be forced to run, all tests will run in the continuous integration.
# on local execution, without run-all, will be allowed to skip if the compiler is not installed
def test_windows_clang_real():

    result = detect_compiler_version(Compiler.CLANG)

    assert result.error is None
    assert result.value is not None
    assert result.value.isdigit()


# =========================================================
# LINUX TESTS
# =========================================================


@pytest.mark.skipif(platform.system().lower() != OS.LINUX.value, reason=OS.LINUX.value + "-only test")
@pytest.mark.requires("g++")  # if run-all this will be forced to run, all tests will run in the continuous integration.
# on local execution, without run-all, will be allowed to skip if the compiler is not installed
def test_linux_gcc_real():

    result = detect_compiler_version(Compiler.GCC)

    assert result.error is None
    assert result.value is not None
    assert result.value.isdigit()


@pytest.mark.skipif(platform.system().lower() != OS.LINUX.value, reason=OS.LINUX.value + "-only test")
@pytest.mark.requires(
    "clang++"
)  # if run-all this will be forced to run, all tests will run in the continuous integration.
# on local execution, without run-all, will be allowed to skip if the compiler is not installed
def test_linux_clang_real():

    result = detect_compiler_version(Compiler.CLANG)

    assert result.error is None
    assert result.value is not None
    assert result.value.isdigit()


# =========================================================
# MACOS TESTS
# =========================================================


@pytest.mark.skipif(platform.system().lower() != OS_PLATFORM_MACOS, reason=OS.MACOS.value + "-only test")
@pytest.mark.requires(
    "clang++"
)  # if run-all this will be forced to run, all tests will run in the continuous integration.
# on local execution, without run-all, will be allowed to skip if the compiler is not installed
def test_macos_apple_clang_real():

    result = detect_compiler_version(Compiler.APPLE_CLANG)

    assert result.error is None
    assert result.value is not None
    assert result.value.isdigit()


# =========================================================
# MOCKED TESTS
# =========================================================


def test_mocked_gcc():

    def runner(_: list[str]) -> str:
        return "g++ (Ubuntu 13.2.0-23ubuntu1) 13.2.0"

    result = detect_compiler_version(Compiler.GCC, runner=runner)

    assert result.error is None
    assert result.value == "13"


def test_mocked_clang():

    def runner(_: list[str]) -> str:
        return "clang version 18.1.0"

    result = detect_compiler_version(Compiler.CLANG, runner=runner)

    assert result.error is None
    assert result.value == "18"


def test_mocked_apple_clang():

    def runner(_: list[str]) -> str:
        return "Apple clang version 16.0.0"

    result = detect_compiler_version(Compiler.APPLE_CLANG, runner=runner)

    assert result.error is None
    assert result.value == "16"


def test_mocked_msvc():

    def runner(_: list[str]) -> str:
        return "Microsoft (R) C/C++ Optimizing Compiler Version 19.38.33135 for x64"

    result = detect_compiler_version(Compiler.MSVC, runner=runner)

    assert result.error is None
    assert result.value == "143"


# =========================================================
# FAILURE TESTS
# =========================================================


def test_invalid_gcc_output():

    def runner(_: list[str]) -> str:
        return "invalid compiler output"

    result = detect_compiler_version(Compiler.GCC, runner=runner)

    assert result.error is not None
    assert result.value is None


def test_invalid_clang_output():

    def runner(_: list[str]) -> str:
        return "invalid compiler output"

    result = detect_compiler_version(Compiler.CLANG, runner=runner)

    assert result.error is not None
    assert result.value is None


def test_invalid_apple_clang_output():

    def runner(_: list[str]) -> str:
        return "invalid compiler output"

    result = detect_compiler_version(Compiler.APPLE_CLANG, runner=runner)

    assert result.error is not None
    assert result.value is None


def test_invalid_msvc_output():

    def runner(_: list[str]) -> str:
        return "invalid compiler output"

    result = detect_compiler_version(Compiler.MSVC, runner=runner)

    assert result.error is not None
    assert result.value is None


def test_detect_compiler_version_run_failure_returncode():

    mock_process = Mock()
    mock_process.returncode = 1
    mock_process.stdout = "failure"

    with patch("subprocess.run", return_value=mock_process):
        result = detect_compiler_version_run(["gcc", "--version"])

        assert result is None


def test_detect_compiler_version_run_exception():

    with patch("subprocess.run", side_effect=Exception("boom")):
        result = detect_compiler_version_run(["gcc"])

        assert result is None


def test_mocked_msvc_142():

    def runner(_: list[str]) -> str:
        return "Microsoft (R) C/C++ Optimizing Compiler Version 19.29.30100 for x64"

    result = detect_compiler_version(Compiler.MSVC, runner=runner)

    assert result.error is None
    assert result.value == "142"


def test_mocked_msvc_fallback_version():

    def runner(_: list[str]) -> str:
        return "Microsoft (R) C/C++ Optimizing Compiler Version 18.10.12345 for x64"

    result = detect_compiler_version(Compiler.MSVC, runner=runner)

    assert result.error is None
    assert result.value == "1810"


def test_unsupported_compiler():

    class FakeCompiler:
        pass

    result = detect_compiler_version(FakeCompiler())  # type: ignore[arg-type]

    assert result.error is not None
    assert result.value is None
