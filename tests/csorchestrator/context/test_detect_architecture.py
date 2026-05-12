# tests/test_detect_architecture.py

from unittest.mock import patch

import pytest

from csorchestrator.context.context_os_architecture import Architecture, detect_architecture

# =========================================================
# X64
# =========================================================


@pytest.mark.parametrize(
    "machine",
    [
        "x86_64",
        "amd64",
        "x64",
    ],
)
def test_detect_architecture_x64(machine):
    with patch("platform.machine", return_value=machine):
        result = detect_architecture()

    assert result.error is None
    assert result.value == (Architecture.X64, "generic")


# =========================================================
# ARM64
# =========================================================


@pytest.mark.parametrize(
    "machine",
    [
        "aarch64",
        "arm64",
    ],
)
def test_detect_architecture_arm64_generic(machine):
    with (
        patch("platform.machine", return_value=machine),
        patch("csorchestrator.context.context_os_architecture.detect_arm64_variant", return_value="generic"),
    ):
        result = detect_architecture()

    assert result.error is None
    assert result.value == (Architecture.ARM64, "generic")


@pytest.mark.parametrize(
    ("variant", "expected"),
    [
        ("orin", "orin"),
        ("xavier", "xavier"),
        ("nano", "nano"),
    ],
)
def test_detect_architecture_arm64_variants(variant, expected):
    with (
        patch("platform.machine", return_value="aarch64"),
        patch("csorchestrator.context.context_os_architecture.detect_arm64_variant", return_value=variant),
    ):
        result = detect_architecture()

    assert result.error is None
    assert result.value == (Architecture.ARM64, expected)


# =========================================================
# UNSUPPORTED
# =========================================================


@pytest.mark.parametrize(
    "machine",
    [
        "i386",
        "armv7l",
        "mips",
        "sparc",
    ],
)
def test_detect_architecture_unsupported(machine):
    with patch("platform.machine", return_value=machine):
        result = detect_architecture()

    assert result.value is None
    assert result.error == f"Unsupported architecture: {machine}"
