import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

from csorchestrator.portable.package_version import PackageVersion


@dataclass
class ManifestVersionsEntry:
    variant: str
    entries: list[PackageVersion] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "variant": self.variant,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ManifestVersionsEntry":
        return cls(
            variant=data["variant"],
            entries=[PackageVersion.from_dict(entry) for entry in data["entries"]],
        )


@dataclass
class ReleaseManifest:
    project_name: str
    project_version: str
    variants: list[ManifestVersionsEntry] = field(default_factory=list)

    MANIFEST_VERSION: ClassVar[str] = "1.0"
    manifest_version: str = MANIFEST_VERSION

    CS_ORCHESTRATOR_MANIFEST_EXTENSION: ClassVar[str] = ".csOrchestratorManifest"
    CS_ORCHESTRATOR_MANIFEST_ROOT: ClassVar[str] = "csOrchestratorManifest"

    def to_dict(self) -> dict[str, Any]:
        return {
            ReleaseManifest.CS_ORCHESTRATOR_MANIFEST_ROOT: {
                "manifest_version": self.manifest_version,
                "project_name": self.project_name,
                "project_version": self.project_version,
                "variants": [variant.to_dict() for variant in self.variants],
            }
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReleaseManifest":
        in_data = data[ReleaseManifest.CS_ORCHESTRATOR_MANIFEST_ROOT]
        return cls(
            manifest_version=in_data["manifest_version"],
            project_name=in_data["project_name"],
            project_version=in_data["project_version"],
            variants=[ManifestVersionsEntry.from_dict(variant) for variant in in_data["variants"]],
        )

    def write_release_manifest(
        self,
        filename: Path,
    ) -> None:
        """Write a release manifest to a JSON file."""
        path = Path(filename)
        # TODO robustify and return possible errors
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)

    @classmethod
    def load_release_manifest(
        cls,
        filename: Path,
    ) -> "ReleaseManifest":
        """Load a release manifest from a JSON file."""
        path = Path(filename)
        # TODO robustify and return possible errors
        with path.open("r", encoding="utf-8") as f:
            return ReleaseManifest.from_dict(json.load(f))
