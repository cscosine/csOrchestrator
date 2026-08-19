import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

from csorchestrator.frontend.step.step_get_versions_from_cmake_config_package_version import CMakeConfigPackageVersion


@dataclass
class ManifestVersionsEntry:
    variant: str
    entries: list[CMakeConfigPackageVersion] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "variant": self.variant,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ManifestVersionsEntry":
        return cls(
            variant=data["variant"],
            entries=[CMakeConfigPackageVersion.from_dict(entry) for entry in data["entries"]],
        )


@dataclass
class Manifest:
    manifest_version: str
    project_name: str
    project_version: str
    variants: list[ManifestVersionsEntry] = field(default_factory=list)

    MANIFEST_VERSION: ClassVar[str] = "1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_version": self.manifest_version,
            "project_name": self.project_name,
            "project_version": self.project_version,
            "variants": [variant.to_dict() for variant in self.variants],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Manifest":
        return cls(
            manifest_version=data["manifest_version"],
            project_name=data["project_name"],
            project_version=data["project_version"],
            variants=[ManifestVersionsEntry.from_dict(variant) for variant in data["variants"]],
        )


def write_release_manifest(
    manifest: Manifest,
    filename: Path,
) -> None:
    """Write a release manifest to a JSON file."""
    path = Path(filename)
    # TODO robustify and return possible errors
    with path.open("w", encoding="utf-8") as f:
        json.dump(manifest.to_dict(), f, indent=2, sort_keys=True)


def load_release_manifest(
    filename: Path,
) -> Manifest:
    """Load a release manifest from a JSON file."""
    path = Path(filename)
    # TODO robustify and return possible errors
    with path.open("r", encoding="utf-8") as f:
        return Manifest.from_dict(json.load(f))
