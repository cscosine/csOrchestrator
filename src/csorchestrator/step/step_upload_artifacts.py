from dataclasses import dataclass
from pathlib import Path

from csorchestrator.ci.github.github_workflow_steps_transations import StepGitHubUploadArtifacts
from csorchestrator.ci.github.guthub_workflow_matrix_constants import (
    create_context_os_architecture_compiler_generator_string_github_matrix,
)
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
)
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import (
    JobOrchestratorMatrixExecution,
    StepBase,
    StepValidatorBase,
    StepValidatorNoOp,
)


def create_artifact_prefix_from_orchestrator_name_version(o: Orchestrator) -> str:
    return f"{o.name}-{o.version}-"


@dataclass
class StepUploadArtifacts(StepBase):
    base_install_dir: Path
    artifact_prefix: str

    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_upload_artifacts(self, context, reporter_sink)

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return step_upload_artifacts_to_githubwf(self, wf_job, reporter_sink)

    @classmethod
    def createValidator(cls) -> StepValidatorBase:
        return StepValidatorNoOp()


def execute_step_upload_artifacts(
    step: StepUploadArtifacts, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    return Report().append_info("Upload artifacts is no-op in local execution")


def step_upload_artifacts_to_githubwf(
    step: StepUploadArtifacts, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:

    install_subdir = create_context_os_architecture_compiler_generator_string_github_matrix()

    artifact_name = f"{step.artifact_prefix}{install_subdir}"

    wf_job.steps.append(
        StepGitHubUploadArtifacts(
            name="Upload Artifacts",
            with_name=artifact_name,
            with_path=(step.base_install_dir / install_subdir / "*.tar.gz").as_posix(),
        )
    )

    return Report()
