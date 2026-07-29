from dataclasses import dataclass
from pathlib import Path

from csorchestrator.domain.orchestrator.orchestrator import Orchestrator
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import (
    StepBase,
)
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.github_workflow_translation.github_workflow_config import JobOrchestratorMatrixExecution
from csorchestrator.frontend.github_workflow_translation.github_workflow_matrix_constants import (
    create_context_os_architecture_compiler_generator_string_github_matrix,
)
from csorchestrator.frontend.github_workflow_translation.github_workflow_steps_transations import (
    StepGitHubUploadArtifacts,
)
from csorchestrator.frontend.github_workflow_translation.orchestrator_visitor_github_wf_generator import (
    StepCapabilityGithubWorkflow,
)
from csorchestrator.frontend.step.step_get_versions_from_cmake_config_package_version import (
    CS_ORCHESTRATOR_VERSION_FILE_EXTENSION,
)


@dataclass
class StepUploadArtifactsCapabilityGithubWorkflow(StepCapabilityGithubWorkflow):
    step: "StepUploadArtifacts"

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return step_upload_artifacts_to_githubwf(self.step, wf_job, reporter_sink)


def create_artifact_prefix_from_orchestrator_name_version(o: Orchestrator) -> str:
    return f"{o.name}-{o.version}-"


@dataclass
class StepUploadArtifacts(StepBase):
    base_install_dir: Path
    artifact_prefix: str

    def __post_init__(self) -> None:
        self.add_capability(StepUploadArtifactsCapabilityGithubWorkflow(self), StepCapabilityGithubWorkflow)


def step_upload_artifacts_to_githubwf(
    step: StepUploadArtifacts, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:

    install_subdir = create_context_os_architecture_compiler_generator_string_github_matrix()

    artifact_name = f"{step.artifact_prefix}{install_subdir}"

    wf_job.steps.append(
        StepGitHubUploadArtifacts(
            name="Upload Artifacts",
            with_name=artifact_name,
            with_path=[
                (step.base_install_dir / install_subdir / "*.tar.gz").as_posix(),
                (step.base_install_dir / ("*" + CS_ORCHESTRATOR_VERSION_FILE_EXTENSION)).as_posix(),
            ],
        )
    )

    return Report()
