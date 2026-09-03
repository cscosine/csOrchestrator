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
from csorchestrator.frontend.github_workflow_translation.github_workflow_steps_transations import (
    CreateGitHubRelease,
    DownloadAllArtifacts,
    ShowDownloadedFiles,
    StepGitHubUploadArtifacts,
)
from csorchestrator.portable.release_manifest import ReleaseManifest


class ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow(ReleaseCreationOnTagConfigBaseCapability):
    # TODO: make virtual methods

    def to_steps_dict(
        self,
        matrix_list: list[ContextOsArchitectureCompilerGenerator],
        orchestrator_description: OrchestratorDescription,
        artifacts_folder: str,
    ) -> list[dict[str, Any]]:
        return []


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
            extra_extension_for_release_files = ReleaseManifest.CS_ORCHESTRATOR_MANIFEST_EXTENSION
            steps.append(
                StepGitHubUploadArtifacts(
                    name="Upload artifacts",
                    with_name="manifest" + extra_extension_for_release_files,
                    with_path=[f"{artifacts_folder}/**/*{extra_extension_for_release_files}"],
                ).to_dict()
            )

        steps.append(CreateGitHubRelease(artifacts_folder, self.if_str, extra_extension_for_release_files).to_dict())

        return {
            self.config.name: {
                "needs": self.needs,
                "runs-on": self.runs_on,
                "permissions": {"contents": "write"},
                "steps": steps,
            }
        }
