import os
from unittest.mock import patch

import pytest

from csorchestrator.context.context_os_architecture import OS, detect_os

# =========================================================
# WINDOWS
# =========================================================


@pytest.mark.skipif(os.name != "nt", reason="Runs only on Windows")
def test_detect_os_real_windows():
    result = detect_os()

    assert result.error is None
    assert result.value is not None

    detected_os, version, distro = result.value

    assert detected_os == OS.WINDOWS
    assert isinstance(version, str)
    assert distro is None


@pytest.mark.skipif(os.name != "nt", reason="Runs only on Windows")
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
    assert result.value == (OS.LINUX, "6.8.0", "ubuntu-22.04")


@pytest.mark.skipif(os.name != "nt", reason="Runs only on Windows")
def test_detect_os_mock_macos_from_windows():
    with (
        patch("platform.system", return_value="Darwin"),
        patch("platform.mac_ver", return_value=("14.5", ("", "", ""), "")),
    ):
        result = detect_os()

    assert result.error is None
    assert result.value == (OS.MACOS, "14.5", None)


# =========================================================
# LINUX
# =========================================================


@pytest.mark.skipif(os.name != "posix", reason="Runs only on Linux/macOS")
@pytest.mark.skipif(
    __import__("platform").system().lower() != "linux",
    reason="Runs only on Linux",
)
def test_detect_os_real_linux():
    result = detect_os()

    assert result.error is None
    assert result.value is not None

    detected_os, kernel_version, distro = result.value

    assert detected_os == OS.LINUX
    assert isinstance(kernel_version, str)
    assert distro is None or isinstance(distro, str)


@pytest.mark.skipif(
    __import__("platform").system().lower() != "linux",
    reason="Runs only on Linux",
)
def test_detect_os_mock_windows_from_linux():
    with (
        patch("platform.system", return_value="Windows"),
        patch("platform.release", return_value="11"),
    ):
        result = detect_os()

    assert result.error is None
    assert result.value == (OS.WINDOWS, "11", None)


@pytest.mark.skipif(
    __import__("platform").system().lower() != "linux",
    reason="Runs only on Linux",
)
def test_detect_os_mock_macos_from_linux():
    with (
        patch("platform.system", return_value="Darwin"),
        patch("platform.mac_ver", return_value=("14.5", ("", "", ""), "")),
    ):
        result = detect_os()

    assert result.error is None
    assert result.value == (OS.MACOS, "14.5", None)


# =========================================================
# MACOS
# =========================================================


@pytest.mark.skipif(
    __import__("platform").system().lower() != "darwin",
    reason="Runs only on macOS",
)
def test_detect_os_real_macos():
    result = detect_os()

    assert result.error is None
    assert result.value is not None

    detected_os, version, distro = result.value

    assert detected_os == OS.MACOS
    assert isinstance(version, str)
    assert distro is None


@pytest.mark.skipif(
    __import__("platform").system().lower() != "darwin",
    reason="Runs only on macOS",
)
def test_detect_os_mock_windows_from_macos():
    with (
        patch("platform.system", return_value="Windows"),
        patch("platform.release", return_value="11"),
    ):
        result = detect_os()

    assert result.error is None
    assert result.value == (OS.WINDOWS, "11", None)


@pytest.mark.skipif(
    __import__("platform").system().lower() != "darwin",
    reason="Runs only on macOS",
)
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
    assert result.value == (OS.LINUX, "6.8.0", "ubuntu-24.04")


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

    assert result.error is None
    assert result.value == (
        OS.LINUX,
        "6.8.0",
        None,
    )


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

    assert result.error is None
    assert result.value == (
        OS.LINUX,
        "6.8.0",
        None,
    )


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

    assert result.error is None
    assert result.value == (
        OS.LINUX,
        "6.8.0",
        None,
    )
