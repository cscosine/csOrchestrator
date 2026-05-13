import platform
from unittest.mock import patch

import pytest

from csorchestrator.context.context_os_architecture import OS, detect_os

# =========================================================
# WINDOWS
# =========================================================


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-only test")
def test_detect_os_real_windows():
    result = detect_os()

    assert result.error is None
    assert result.value is not None

    detected_os, version = result.value

    assert detected_os == OS.WINDOWS
    assert version[0] == "v"


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-only test")
def test_detect_os_mock_linux_from_windows():
    os_release_content = """
ID=ubuntu
VERSION_ID="22.04"
"""

    with (
        patch("platform.system", return_value="Linux"),
        patch("platform.release", return_value="6.8.0"),
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.read_text", return_value=os_release_content),
    ):
        result = detect_os()

    assert result.error is None
    assert result.value == (OS.LINUX, "ubuntu22.04")


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-only test")
def test_detect_os_mock_macos_from_windows():
    with (
        patch("platform.system", return_value="Darwin"),
        patch("platform.mac_ver", return_value=("14.5", ("", "", ""), "")),
    ):
        result = detect_os()

    assert result.error is None
    assert result.value == (OS.MACOS, "v14.5")


# =========================================================
# LINUX
# =========================================================


@pytest.mark.skipif(platform.system() != "Linux", reason="Linux-only test")
def test_detect_os_real_linux():
    result = detect_os()

    assert result.error is None
    assert result.value is not None

    detected_os, distro = result.value

    assert detected_os == OS.LINUX
    assert distro != ""


@pytest.mark.skipif(platform.system() != "Linux", reason="Linux-only test")
def test_detect_os_mock_windows_from_linux():
    with (
        patch("platform.system", return_value="Windows"),
        patch("platform.release", return_value="11"),
    ):
        result = detect_os()

    assert result.error is None
    assert result.value == (OS.WINDOWS, "v11")


@pytest.mark.skipif(platform.system() != "Linux", reason="Linux-only test")
def test_detect_os_mock_macos_from_linux():
    with (
        patch("platform.system", return_value="Darwin"),
        patch("platform.mac_ver", return_value=("14.5", ("", "", ""), "")),
    ):
        result = detect_os()

    assert result.error is None
    assert result.value == (OS.MACOS, "v14.5")


# =========================================================
# MACOS
# =========================================================


@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-only test")
def test_detect_os_real_macos():
    result = detect_os()

    assert result.error is None
    assert result.value is not None

    detected_os, version = result.value

    assert detected_os == OS.MACOS
    assert version[0] == "v"


@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-only test")
def test_detect_os_mock_windows_from_macos():
    with (
        patch("platform.system", return_value="Windows"),
        patch("platform.release", return_value="11"),
    ):
        result = detect_os()

    assert result.error is None
    assert result.value == (OS.WINDOWS, "v11")


@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-only test")
def test_detect_os_mock_linux_from_macos():
    os_release_content = """
ID=ubuntu
VERSION_ID="24.04"
"""

    with (
        patch("platform.system", return_value="Linux"),
        patch("platform.release", return_value="6.8.0"),
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.read_text", return_value=os_release_content),
    ):
        result = detect_os()

    assert result.error is None
    assert result.value == (OS.LINUX, "ubuntu24.04")


# =========================================================
# UNSUPPORTED OS
# =========================================================


def test_detect_os_unsupported():
    with patch("platform.system", return_value="Solaris"):
        result = detect_os()

    assert result.value is None
    assert result.error == "Unsupported OS: solaris"


# =========================================================
# LINUX EDGE CASES
# =========================================================


def test_detect_os_linux_without_os_release():
    with (
        patch("platform.system", return_value="Linux"),
        patch("platform.release", return_value="6.8.0"),
        patch("pathlib.Path.exists", return_value=False),
    ):
        result = detect_os()

    assert result.error is not None


def test_detect_os_linux_missing_version_id():
    os_release_content = """
ID=ubuntu
"""

    with (
        patch("platform.system", return_value="Linux"),
        patch("platform.release", return_value="6.8.0"),
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.read_text", return_value=os_release_content),
    ):
        result = detect_os()

    assert result.error is not None


def test_detect_os_linux_missing_both_id_and_version():
    os_release_content = """
NAME="Ubuntu"
PRETTY_NAME="Ubuntu 24.04"
"""

    with (
        patch("platform.system", return_value="Linux"),
        patch("platform.release", return_value="6.8.0"),
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.read_text", return_value=os_release_content),
    ):
        result = detect_os()

    assert result.error is not None
