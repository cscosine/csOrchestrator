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
    os_distro: str

    architecture: Architecture
    architecture_variant: str  # generic orin xavier nano


# =========================================================
# OS / ARCH DETECTION
# =========================================================


# return the os name if not supported
def detect_os() -> Expected[tuple[OS, str, str | None], str]:

    system = platform.system().lower()

    # -----------------------------------------------------
    # WINDOWS
    # -----------------------------------------------------

    if system == "windows":
        version = platform.release()

        return Expected[tuple[OS, str, str | None], str].make_value((OS.WINDOWS, version, None))

    # -----------------------------------------------------
    # LINUX
    # -----------------------------------------------------

    if system == "linux":
        distro = None

        os_release = Path("/etc/os-release")

        if os_release.exists():
            content = os_release.read_text()

            distro_match = re.search(r'^ID="?([^"\n]+)"?', content, re.MULTILINE)
            version_match = re.search(r'^VERSION_ID="?([^"\n]+)"?', content, re.MULTILINE)

            if distro_match and version_match:
                distro = distro_match.group(1).lower() + "-" + version_match.group(1).lower()

        kernel_version = platform.release()

        return Expected[tuple[OS, str, str | None], str].make_value((OS.LINUX, kernel_version, distro))

    if system == "darwin":
        return Expected[tuple[OS, str, str | None], str].make_value((OS.MACOS, platform.mac_ver()[0], None))

    return Expected[tuple[OS, str, str | None], str].make_error(f"Unsupported OS: {system}")


def detect_architecture() -> Expected[tuple[Architecture, str], str]:

    machine = platform.machine().lower()

    # -----------------------------------------------------
    # X64
    # -----------------------------------------------------

    if machine in ["amd64", "x86_64", "x64"]:
        return Expected[tuple[Architecture, str], str].make_value((Architecture.X64, "generic"))

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
            print(f"@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Detected ARM64 model: {model}")

            if "orin" in model:
                return "orin"

            if "xavier" in model:
                return "xavier"

            if "nano" in model:
                return "nano"

        except Exception:
            pass

    return "generic"


# =========================================================
# PUBLIC API
# =========================================================


def detect_context_os_architecture() -> Expected[ContextOsArchitecture, str]:

    os_result = detect_os()
    if os_result.error is not None:
        return Expected[ContextOsArchitecture, str].make_error(os_result.error)

    assert os_result.value is not None  # to make mypy happy need to check for None explicitly
    os_value, os_version, distro = os_result.value

    arch_result = detect_architecture()
    if arch_result.error is not None:
        return Expected[ContextOsArchitecture, str].make_error(arch_result.error)

    assert arch_result.value is not None
    arch, arch_variant = arch_result.value

    return Expected[ContextOsArchitecture, str].make_value(
        ContextOsArchitecture(
            os=os_value,
            os_version=os_version,
            os_distro=distro if distro is not None else "",
            architecture=arch,
            architecture_variant=arch_variant,
        )
    )
