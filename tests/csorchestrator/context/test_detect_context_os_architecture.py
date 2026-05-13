from unittest.mock import patch

from csorchestrator.context.context_os_architecture import (
    OS,
    Architecture,
    ContextOsArchitecture,
    detect_context_os_architecture,
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
                    "ubuntu24.04",
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
        result = detect_context_os_architecture()

    assert result.error is None

    assert result.value == ContextOsArchitecture(
        os=OS.LINUX,
        os_version="ubuntu24.04",
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
        result = detect_context_os_architecture()

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
                    "ubuntu24.04",
                )
            ),
        ),
        patch(
            "csorchestrator.context.context_os_architecture.detect_architecture",
            return_value=Expected.make_error("Unsupported architecture"),
        ),
    ):
        result = detect_context_os_architecture()

    assert result.value is None
    assert result.error == "Unsupported architecture"
