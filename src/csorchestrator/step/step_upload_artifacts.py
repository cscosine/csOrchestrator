from dataclasses import dataclass
from pathlib import Path

from csorchestrator.ci.github.github_workflow_config import (
    JobDescription,
    MatrixOsArchCompilerGeneratorRunnerEntryInclude,
    StepGithubUploadArtifacts,
)
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
)
from csorchestrator.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string_from_components,
)
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase


@dataclass
class StepUploadArtifacts(StepBase):
    base_install_dir: Path


def execute_step_upload_artifacts(
    step: StepUploadArtifacts, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    return Report().append_info("Upload artifacts is no-op in local execution")


def step_upload_artifacts_to_githubwf(
    step: StepUploadArtifacts, wf_job: JobDescription, reporter_sink: ReporterSinkBase
) -> Report:

    install_subdir = create_context_os_architecture_compiler_generator_string_from_components(
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_NAME_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_VERSION_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_ARCHITECTURE_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_ARCHITECTURE_VARIANT_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_COMPILER_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_COMPILER_VERSION_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_GENERATOR_EMBRACED,
    )

    artifact_name = f"{wf_job.orchestrator_desc.name}-{wf_job.orchestrator_desc.version}-{install_subdir}"

    wf_job.steps.append(
        StepGithubUploadArtifacts(
            name="Upload Artifacts",
            with_name=artifact_name,
            with_path=str(step.base_install_dir / install_subdir / "*.tar.gz"),
        )
    )

    return Report()


def validate_step_upload_artifacts(step: StepUploadArtifacts) -> Report:
    report = Report()
    return report
