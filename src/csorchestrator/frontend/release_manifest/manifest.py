import json
from dataclasses import dataclass, field
from pathlib import Path

from csorchestrator.frontend.step.step_get_versions_from_cmake_config_package_version import CMakeConfigPackageVersion


@dataclass
class ManifestVersionsEntry:
    variant_string_description: str
    entries: list[CMakeConfigPackageVersion] = field(default_factory=list)


# return smt like
# {
#   "variant1": [
#     {"name": "foo", "version": "1.2.3"}
#   ],
#   "variant2": [
#     {"name": "bar", "version": "2.0.0"}
#   ]
# }
def create_release_manifest(
    entries: list[ManifestVersionsEntry],
) -> dict[str, list[dict[str, str]]]:
    return {
        entry.variant_string_description: [{"name": pv.name, "version": pv.version} for pv in entry.entries]
        for entry in entries
    }


def write_release_manifest(
    manifest: dict[str, list[dict[str, str]]],
    filename: Path,
) -> None:
    """Write a release manifest to a JSON file."""
    path = Path(filename)
    with path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


def load_release_manifest(
    filename: Path,
) -> dict[str, list[dict[str, str]]]:
    """Load a release manifest from a JSON file."""
    path = Path(filename)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
