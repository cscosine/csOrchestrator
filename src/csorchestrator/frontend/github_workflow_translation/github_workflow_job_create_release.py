from dataclasses import dataclass

from csorchestrator.domain.context.context_os_architecture_compiler_generator import (
    ContextOsArchitectureCompilerGenerator,
)
from csorchestrator.domain.orchestrator.orchestrator import OrchestratorDescription
from csorchestrator.domain.orchestrator.workflow_config import (
    ReleaseCreationOnTagConfigBase,
    ReleaseCreationOnTagConfigBaseCapability,
)
from csorchestrator.foundation.core.strings_utils import string_indent


class ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow(ReleaseCreationOnTagConfigBaseCapability):
    def to_githubwf_lines(
        self,
        matrix_list: list[ContextOsArchitectureCompilerGenerator],
        orchestrator_description: OrchestratorDescription,
        artifacts_folder: str,
    ) -> list[str]:
        return []

    def getReleaseFilesExtension(self) -> str | None:
        return None


@dataclass
class JobReleaseCreationFromArtifacts:
    config: ReleaseCreationOnTagConfigBase
    needs: str
    matrix_list: list[ContextOsArchitectureCompilerGenerator]
    orchestrator_description: OrchestratorDescription
    runs_on: str
    if_str: str


def job_release_on_tag_to_string_lines(job: JobReleaseCreationFromArtifacts, indent: int = 0) -> list[str]:
    artifacts_folder = "artifacts"

    capability = job.config.get_capability(ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow)
    add_lines = []
    if capability is not None:
        add_lines = capability.to_githubwf_lines(job.matrix_list, job.orchestrator_description, artifacts_folder)

    line_list = [f"{string_indent(indent)}{job.config.name}:"]
    line_list += [f"{string_indent(indent + 2)}needs: {job.needs}"]
    line_list += [f"{string_indent(indent + 2)}runs-on: {job.runs_on}"]
    line_list += [""]
    line_list += [""]
    line_list += [f"{string_indent(indent + 2)}permissions:"]
    line_list += [f"{string_indent(indent + 4)}contents: write"]
    line_list += [""]
    line_list += [f"{string_indent(indent + 2)}steps:"]
    line_list += [f"{string_indent(indent + 4)}- name: Download all artifacts"]
    line_list += [f"{string_indent(indent + 6)}uses: actions/download-artifact@v8"]
    line_list += [f"{string_indent(indent + 6)}with:"]
    line_list += [f"{string_indent(indent + 8)}path: {artifacts_folder}"]
    line_list += [""]
    line_list += [f"{string_indent(indent + 4)}- name: Show downloaded files"]
    line_list += [f"{string_indent(indent + 6)}run: find {artifacts_folder} -type f"]
    line_list += [""]
    if len(add_lines) > 0:
        for line in add_lines:
            if line != "":
                line_list += [f"{string_indent(indent + 4)}{line}"]
            else:
                line_list += [""]

    if capability is not None:
        ext = capability.getReleaseFilesExtension()
        if ext is not None:
            line_list += [f"{string_indent(indent + 4)}- name: Upload manifest"]
            line_list += [f"{string_indent(indent + 4)}  uses: actions/upload-artifact@v4"]
            line_list += [f"{string_indent(indent + 4)}  with:"]
            line_list += [f"{string_indent(indent + 4)}    name: manifest" + ext]
            line_list += [f"{string_indent(indent + 4)}    path: artifacts/**/*" + ext]
            line_list += [""]

    line_list += [f"{string_indent(indent + 4)}- name: Create GitHub Release"]
    line_list += [f"{string_indent(indent + 6)}if: {job.if_str}"]
    line_list += [f"{string_indent(indent + 6)}uses: softprops/action-gh-release@v3"]
    line_list += [f"{string_indent(indent + 6)}with:"]
    line_list += [f"{string_indent(indent + 8)}files: |"]
    line_list += [f"{string_indent(indent + 10)}{artifacts_folder}/**/*.tar.gz"]
    if capability is not None:
        ext = capability.getReleaseFilesExtension()
        if ext is not None:
            line_list += [f"{string_indent(indent + 10)}{artifacts_folder}/**/*" + ext]
    line_list += [""]
    return line_list
