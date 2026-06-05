from unittest.mock import patch

from csorchestrator.context.context_os_architecture import (
    ARCHITECTURE_VARIANT_ARM64_ORIN,
    ARCHITECTURE_VARIANT_ARM64_XAVIER,
    OS,
    UBUNTU_VERSIONS,
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
                    UBUNTU_VERSIONS.UBUNTU_24_04.value,
                )
            ),
        ),
        patch(
            "csorchestrator.context.context_os_architecture.detect_architecture",
            return_value=Expected.make_value(
                (
                    Architecture.ARM64,
                    ARCHITECTURE_VARIANT_ARM64_ORIN,
                )
            ),
        ),
    ):
        result = detect_context_os_architecture()

    assert result.error is None

    assert result.value == ContextOsArchitecture(
        os=OS.LINUX,
        os_version=UBUNTU_VERSIONS.UBUNTU_24_04.value,
        architecture=Architecture.ARM64,
        architecture_variant=ARCHITECTURE_VARIANT_ARM64_ORIN,
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
                    UBUNTU_VERSIONS.UBUNTU_24_04,
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


# test can be executed on
def test_context_os_architecture_can_be_executed_on():
    a1 = ContextOsArchitecture(
        os=OS.LINUX,
        os_version=UBUNTU_VERSIONS.UBUNTU_24_04.value,
        architecture=Architecture.ARM64,
        architecture_variant=ARCHITECTURE_VARIANT_ARM64_ORIN,
    )
    a2 = ContextOsArchitecture(
        os=OS.LINUX,
        os_version=UBUNTU_VERSIONS.UBUNTU_24_04.value,
        architecture=Architecture.ARM64,
        architecture_variant=ARCHITECTURE_VARIANT_ARM64_ORIN,
    )
    a3 = ContextOsArchitecture(
        os=OS.LINUX,
        os_version=UBUNTU_VERSIONS.UBUNTU_24_04.value,
        architecture=Architecture.ARM64,
        architecture_variant=ARCHITECTURE_VARIANT_ARM64_XAVIER,
    )

    assert a1.can_be_executed_on(a2)
    assert not a1.can_be_executed_on(a3)
