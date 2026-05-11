from dataclasses import dataclass
from enum import Enum


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
    os_distro_version: str

    architecture: Architecture
    architecture_variant: str  # generic orin xavier nano
