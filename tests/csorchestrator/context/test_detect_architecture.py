# tests/test_detect_architecture.py

from unittest.mock import patch

import pytest

from csorchestrator.context.context_os_architecture import (
    ARCHITECTURE_VARIANT_ARM64_NANO,
    ARCHITECTURE_VARIANT_ARM64_ORIN,
    ARCHITECTURE_VARIANT_ARM64_XAVIER,
    ARCHITECTURE_VARIANT_GENERIC,
    Architecture,
    MachineArchitecture,
    detect_architecture,
)

# =========================================================
# X64
# =========================================================


@pytest.mark.parametrize(
    "machine",
    [
        MachineArchitecture.X86_64.value,
        MachineArchitecture.AMD64.value,
        MachineArchitecture.X64.value,
    ],
)
def test_detect_architecture_x64(machine):
    with patch("platform.machine", return_value=machine):
        result = detect_architecture()

    assert result.error is None
    assert result.value == (Architecture.X64, ARCHITECTURE_VARIANT_GENERIC)


# =========================================================
# ARM64
# =========================================================


@pytest.mark.parametrize(
    "machine",
    [
        MachineArchitecture.AARCH64.value,
        MachineArchitecture.ARM64.value,
    ],
)
def test_detect_architecture_arm64_generic(machine):
    with (
        patch("platform.machine", return_value=machine),
        patch(
            "csorchestrator.context.context_os_architecture.detect_arm64_variant",
            return_value=ARCHITECTURE_VARIANT_GENERIC,
        ),
    ):
        result = detect_architecture()

    assert result.error is None
    assert result.value == (Architecture.ARM64, ARCHITECTURE_VARIANT_GENERIC)


@pytest.mark.parametrize(
    ("variant", "expected"),
    [
        (ARCHITECTURE_VARIANT_ARM64_ORIN, ARCHITECTURE_VARIANT_ARM64_ORIN),
        (ARCHITECTURE_VARIANT_ARM64_XAVIER, ARCHITECTURE_VARIANT_ARM64_XAVIER),
        (ARCHITECTURE_VARIANT_ARM64_NANO, ARCHITECTURE_VARIANT_ARM64_NANO),
    ],
)
def test_detect_architecture_arm64_variants(variant, expected):
    with (
        patch("platform.machine", return_value=MachineArchitecture.AARCH64.value),
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
