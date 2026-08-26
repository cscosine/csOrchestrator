from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from csorchestrator.domain.context.context_os_architecture_compiler_generator import (
    ContextOsArchitectureCompilerGenerator,
)
from csorchestrator.domain.orchestrator.orchestrator import OrchestratorDescription
from csorchestrator.domain.orchestrator.workflow_config import (
    ReleaseCreationOnTagConfigBase,
    ReleaseCreationOnTagConfigBaseCapability,
)
from csorchestrator.frontend.github_workflow_translation.YamlStringDumper import (
    LiteralString,
)


class ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow(ReleaseCreationOnTagConfigBaseCapability):
    # TODO: make virtual methods

    def to_steps_dict(
        self,
        matrix_list: list[ContextOsArchitectureCompilerGenerator],
        orchestrator_description: OrchestratorDescription,
        artifacts_folder: str,
    ) -> list[dict[str, Any]]:
        return []

    # TODO abstract? but not compatible with concrete class required by capability
    def getReleaseFilesExtension(self) -> str:
        return ""


class Step(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass


@dataclass(frozen=True)
class DownloadAllArtifacts(Step):
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
class ShowDownloadedFiles(Step):
    artifacts_folder: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": "Show downloaded files",
            "run": f"find {self.artifacts_folder} -type f",
        }


@dataclass(frozen=True)
class CreateGitHubRelease(Step):
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
                "files": extension_files,
            },
        }
        ret["if"] = self.if_str

        return ret


@dataclass(
    frozen=True,
)
class StepGitHubUploadArtifactsNew(Step):
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


@dataclass
class JobReleaseCreationFromArtifacts:
    config: ReleaseCreationOnTagConfigBase
    needs: str
    matrix_list: list[ContextOsArchitectureCompilerGenerator]
    orchestrator_description: OrchestratorDescription
    runs_on: str
    if_str: str

    def to_dict(self) -> dict[str, Any]:
        artifacts_folder = "artifacts"

        steps = [
            DownloadAllArtifacts(artifacts_folder).to_dict(),
            ShowDownloadedFiles(artifacts_folder).to_dict(),
        ]

        capability = self.config.get_capability(ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow)
        extra_extension_for_release_files = None
        if capability is not None:
            steps.extend(capability.to_steps_dict(self.matrix_list, self.orchestrator_description, artifacts_folder))
            extra_extension_for_release_files = capability.getReleaseFilesExtension()
            steps.append(
                StepGitHubUploadArtifactsNew(
                    name="Upload artifacts",
                    with_name="manifest" + extra_extension_for_release_files,
                    with_path=[f"{artifacts_folder}/**/*{extra_extension_for_release_files}"],
                ).to_dict()
            )

        steps.append(CreateGitHubRelease(artifacts_folder, self.if_str, extra_extension_for_release_files).to_dict())

        return {
            "name": self.config.name,
            "needs": self.needs,
            "runs-on": self.runs_on,
            "permissions": {"contents": "write"},
            "steps": steps,
        }
