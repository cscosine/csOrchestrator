from dataclasses import dataclass, field
from typing import Any

from csorchestrator.frontend.github_workflow_translation.github_steps import StepToDictInterface
from csorchestrator.frontend.github_workflow_translation.yaml_string_dumper import LiteralString

# =========================================================
# Steps models
# =========================================================


@dataclass
class StepGitHubAction(StepToDictInterface):
    name: str
    uses: str
    id: str | None = None
    if_str: str | None = None
    with_list: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        ret: dict[str, Any] = {"name": self.name}
        if self.id is not None:
            ret["id"] = self.id
        ret["uses"] = self.uses
        if self.if_str is not None:
            ret["if"] = self.if_str
        if len(self.with_list) > 0:
            ret["with"] = self.with_list

        return ret


@dataclass
class StepCheckoutRepositoryWith:
    repository: str | None
    path: str | None
    ref: str | None
    fetch_depth: str | None
    token: str | None

    def to_dict(self) -> dict[str, Any] | None:

        ret: dict[str, Any] = {}

        if self.repository:
            ret["repository"] = self.repository
        if self.path:
            ret["path"] = self.path
        if self.ref:
            ret["ref"] = self.ref
        if self.fetch_depth:
            ret["fetch-depth"] = self.fetch_depth
        if self.token:
            ret["token"] = self.token

        if len(ret.items()) == 0:
            return None
        return ret


@dataclass(frozen=True, slots=True)
class StepCheckoutRepository(StepToDictInterface):
    name: str
    uses: str = "actions/checkout@v6"
    with_step: StepCheckoutRepositoryWith | None = None

    def to_dict(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "name": self.name,
            "uses": self.uses,
        }

        with_opt = None
        if self.with_step is not None:
            with_opt = self.with_step.to_dict()

        if with_opt is not None:
            ret["with"] = with_opt

        return ret


@dataclass(frozen=True, slots=True)
class StepRunCommand(StepToDictInterface):
    name: str
    run: list[str]
    id: str | None = None
    if_str: str | None = None
    shell_type: str | None = None
    env: list[str] | None = None
    working_directory: str | None = None

    def to_dict(self) -> dict[str, Any]:
        step_dict: dict[str, Any] = {
            "name": self.name,
            "run": LiteralString("\n".join(self.run)),
        }

        if self.id is not None:
            step_dict["id"] = self.id

        if self.if_str is not None:
            step_dict["if"] = self.if_str

        if self.shell_type is not None:
            step_dict["shell"] = self.shell_type

        if self.env is not None and len(self.env) > 0:
            env_dict: dict[str, str] = {}
            for line in self.env:
                key, value = line.split("=", 1)
                env_dict[key.strip()] = value.strip()
            step_dict["env"] = env_dict

        if self.working_directory is not None:
            step_dict["working-directory"] = self.working_directory

        return step_dict


@dataclass(frozen=True)
class DownloadAllArtifacts(StepToDictInterface):
    artifacts_folder: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": "Download all artifacts",
            "uses": "actions/download-artifact@v8",
            "with": {
                "path": self.artifacts_folder,
            },
        }


@dataclass(frozen=True)
class ShowDownloadedFiles(StepToDictInterface):
    artifacts_folder: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": "Show downloaded files",
            "run": f"find {self.artifacts_folder} -type f",
        }


@dataclass(frozen=True)
class CreateGitHubRelease(StepToDictInterface):
    artifacts_folder: str
    if_str: str
    extra_extension_for_release_files: str | None

    def to_dict(self) -> dict[str, Any]:
        extension_files = [f"{self.artifacts_folder}/**/*.tar.gz"]
        if self.extra_extension_for_release_files is not None:
            extension_files.append(f"{self.artifacts_folder}/**/*{self.extra_extension_for_release_files}")

        ret: dict[str, Any] = {
            "name": "Create GitHub Release",
            "uses": "softprops/action-gh-release@v3",
            "with": {
                "files": LiteralString("\n".join(extension_files)),
            },
        }
        ret["if"] = self.if_str

        return ret


@dataclass(
    frozen=True,
)
class StepGitHubUploadArtifacts(StepToDictInterface):
    name: str
    with_name: str
    with_path: list[str]
    uses: str = "actions/upload-artifact@v7"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "uses": self.uses,
            "with": {
                "name": self.with_name,
                "path": LiteralString("\n".join(self.with_path)),
            },
        }
