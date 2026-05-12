# tests/test_detect_context_os_architecture.py

from unittest.mock import patch

from csorchestrator.context.context_os_architecture import (
    OS,
    Architecture,
    ContextOsArchitecture,
    detectContextOsArchitecture,
)
from csorchestrator.core.expected import Expected

# =========================================================
# SUCCESS
# =========================================================


def test_detect_context_os_architecture_success():
    with (
        patch(
            "csorchestrator.context.context_os_architecture.detect_os",
            return_value=Expected.make_value(
                (
                    OS.LINUX,
                    "6.8.0",
                    "ubuntu-24.04",
                )
            ),
        ),
        patch(
            "csorchestrator.context.context_os_architecture.detect_architecture",
            return_value=Expected.make_value(
                (
                    Architecture.ARM64,
                    "orin",
                )
            ),
        ),
    ):
        result = detectContextOsArchitecture()

    assert result.error is None

    assert result.value == ContextOsArchitecture(
        os=OS.LINUX,
        os_version="6.8.0",
        os_distro="ubuntu-24.04",
        architecture=Architecture.ARM64,
        architecture_variant="orin",
    )


# =========================================================
# OS ERROR
# =========================================================


def test_detect_context_os_architecture_os_error():
    with patch(
        "csorchestrator.context.context_os_architecture.detect_os",
        return_value=Expected.make_error("Unsupported OS"),
    ):
        result = detectContextOsArchitecture()

    assert result.value is None
    assert result.error == "Unsupported OS"


# =========================================================
# ARCHITECTURE ERROR
# =========================================================


def test_detect_context_os_architecture_architecture_error():
    with (
        patch(
            "csorchestrator.context.context_os_architecture.detect_os",
            return_value=Expected.make_value(
                (
                    OS.LINUX,
                    "6.8.0",
                    "ubuntu-24.04",
                )
            ),
        ),
        patch(
            "csorchestrator.context.context_os_architecture.detect_architecture",
            return_value=Expected.make_error("Unsupported architecture"),
        ),
    ):
        result = detectContextOsArchitecture()

    assert result.value is None
    assert result.error == "Unsupported architecture"


# =========================================================
# NONE DISTRO VALUES -> EMPTY STRINGS
# =========================================================


def test_detect_context_os_architecture_none_distro_values():
    with (
        patch(
            "csorchestrator.context.context_os_architecture.detect_os",
            return_value=Expected.make_value(
                (
                    OS.WINDOWS,
                    "11",
                    None,
                )
            ),
        ),
        patch(
            "csorchestrator.context.context_os_architecture.detect_architecture",
            return_value=Expected.make_value(
                (
                    Architecture.X64,
                    "generic",
                )
            ),
        ),
    ):
        result = detectContextOsArchitecture()

    assert result.error is None

    assert result.value == ContextOsArchitecture(
        os=OS.WINDOWS,
        os_version="11",
        os_distro="",
        architecture=Architecture.X64,
        architecture_variant="generic",
    )
