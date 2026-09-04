from dataclasses import dataclass
from typing import Any

from csorchestrator.domain.orchestrator.workflow_config import (
    ReleaseCreationOnTagConfigBase,
    ReleaseCreationOnTagConfigBaseCapability,
)
from csorchestrator.frontend.github_workflow_translation.github_workflow_steps_translations import (
    CreateGitHubRelease,
    DownloadAllArtifacts,
    ShowDownloadedFiles,
    StepCheckoutRepository,
    StepGitHubUploadArtifacts,
)
from csorchestrator.frontend.github_workflow_translation.release_creation_context import ReleaseCreationContext
from csorchestrator.portable.release_manifest import ReleaseManifest


class ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow(ReleaseCreationOnTagConfigBaseCapability):
    # TODO: make virtual methods

    def to_steps_dict(self, release_creation_context: ReleaseCreationContext) -> list[dict[str, Any]]:
        return []


@dataclass
class JobReleaseCreationFromArtifacts:
    config: ReleaseCreationOnTagConfigBase
    needs: str
    release_creation_context: ReleaseCreationContext
    runs_on: str
    if_str: str
    self_checkout_repo: bool = True

    def to_dict(self) -> dict[str, Any]:

        steps = []

        if self.self_checkout_repo:
            steps += [
                StepCheckoutRepository(
                    name="Repo Self Checkout",
                ).to_dict(),
            ]

        steps += [
            DownloadAllArtifacts(self.release_creation_context.artifacts_folder).to_dict(),
            ShowDownloadedFiles(self.release_creation_context.artifacts_folder).to_dict(),
        ]

        capability = self.config.get_capability(ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow)
        extra_extension_for_release_files = None
        if capability is not None:
            steps.extend(capability.to_steps_dict(self.release_creation_context))
            extra_extension_for_release_files = ReleaseManifest.CS_ORCHESTRATOR_MANIFEST_EXTENSION
            steps.append(
                StepGitHubUploadArtifacts(
                    name="Upload artifacts",
                    with_name="manifest" + extra_extension_for_release_files,
                    with_path=[
                        f"{self.release_creation_context.artifacts_folder}/**/*{extra_extension_for_release_files}"
                    ],
                ).to_dict()
            )

        steps.append(
            CreateGitHubRelease(
                self.release_creation_context.artifacts_folder, self.if_str, extra_extension_for_release_files
            ).to_dict()
        )

        return {
            self.config.name: {
                "needs": self.needs,
                "runs-on": self.runs_on,
                "permissions": {"contents": "write"},
                "steps": steps,
            }
        }
