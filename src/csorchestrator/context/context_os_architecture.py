import platform
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from csorchestrator.core.expected import Expected


class OS(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"


class Architecture(Enum):
    X64 = "x64"
    ARM64 = "arm64"


@dataclass(frozen=True)
class ContextOsArchitecture:
    os: OS
    os_version: str

    architecture: Architecture
    architecture_variant: str  # generic orin xavier nano

    ARCHITECTURE_VARIANT_GENERIC: str = "generic"

    def is_equal_to(self, other: "ContextOsArchitecture") -> bool:
        return (
            self.os == other.os
            and self.os_version == other.os_version
            and self.architecture == other.architecture
            and self.architecture_variant == other.architecture_variant
        )


# =========================================================
# OS / ARCH DETECTION
# =========================================================


# return the os name if not supported in the expected
def detect_os() -> Expected[tuple[OS, str], str]:

    system = platform.system().lower()

    # -----------------------------------------------------
    # WINDOWS
    # -----------------------------------------------------

    if system == "windows":
        version = platform.release()

        return Expected[tuple[OS, str], str].make_value((OS.WINDOWS, "v" + version))

    # -----------------------------------------------------
    # LINUX
    # -----------------------------------------------------

    if system == "linux":
        os_release = Path("/etc/os-release")

        if os_release.exists():
            content = os_release.read_text()

            distro_match = re.search(r'^ID="?([^"\n]+)"?', content, re.MULTILINE)
            version_match = re.search(r'^VERSION_ID="?([^"\n]+)"?', content, re.MULTILINE)

            if distro_match and version_match:
                distro = distro_match.group(1).lower() + version_match.group(1).lower()
                return Expected[tuple[OS, str], str].make_value((OS.LINUX, distro))
            else:
                return Expected[tuple[OS, str], str].make_error(f"Unsupported linux with /etc/os-release: {content}")

    if system == "darwin":
        version = platform.mac_ver()[0]
        return Expected[tuple[OS, str], str].make_value((OS.MACOS, "v" + version))

    return Expected[tuple[OS, str], str].make_error(f"Unsupported OS: {system}")


def detect_architecture() -> Expected[tuple[Architecture, str], str]:

    machine = platform.machine().lower()

    # -----------------------------------------------------
    # X64
    # -----------------------------------------------------

    if machine in ["amd64", "x86_64", "x64"]:
        return Expected[tuple[Architecture, str], str].make_value(
            (Architecture.X64, ContextOsArchitecture.ARCHITECTURE_VARIANT_GENERIC)
        )

    # -----------------------------------------------------
    # ARM64
    # -----------------------------------------------------

    if machine in ["aarch64", "arm64"]:
        variant = detect_arm64_variant()

        return Expected[tuple[Architecture, str], str].make_value((Architecture.ARM64, variant))

    return Expected[tuple[Architecture, str], str].make_error(f"Unsupported architecture: {machine}")


def detect_arm64_variant() -> str:

    # -----------------------------------------------------
    # NVIDIA JETSON DETECTION
    # -----------------------------------------------------

    model_file = Path("/proc/device-tree/model")

    if model_file.exists():
        try:
            model = model_file.read_text().lower()

            if "orin" in model:
                return "orin"

            if "xavier" in model:
                return "xavier"

            if "nano" in model:
                return "nano"

        except Exception:
            pass

    return ContextOsArchitecture.ARCHITECTURE_VARIANT_GENERIC


# =========================================================
# PUBLIC API
# =========================================================


def detect_context_os_architecture() -> Expected[ContextOsArchitecture, str]:

    os_result = detect_os()
    if os_result.error is not None:
        return Expected[ContextOsArchitecture, str].make_error(os_result.error)

    assert os_result.value is not None  # to make mypy happy need to check for None explicitly
    os_value, os_version = os_result.value

    arch_result = detect_architecture()
    if arch_result.error is not None:
        return Expected[ContextOsArchitecture, str].make_error(arch_result.error)

    assert arch_result.value is not None
    arch, arch_variant = arch_result.value

    return Expected[ContextOsArchitecture, str].make_value(
        ContextOsArchitecture(
            os=os_value,
            os_version=os_version,
            architecture=arch,
            architecture_variant=arch_variant,
        )
    )
