import json
import tarfile
from dataclasses import dataclass
from pathlib import Path

from csorchestrator.ci.github.github_workflow_config import (
    JobDescription,
    MatrixOsArchCompilerGeneratorRunnerEntryInclude,
    StepRunCommand,
)
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
    ContextLocalExecutionActiveMatrixConfig,
)
from csorchestrator.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string,
    create_context_os_architecture_compiler_generator_string_from_components,
)
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase


@dataclass
class StepCreateArchives(StepBase):
    input_id: str
    input_dict: str
    base_install_dir: Path


def execute_step_create_archives(
    step: StepCreateArchives, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    matrix_config = context.get_extra(ContextLocalExecutionActiveMatrixConfig)
    if matrix_config is None:
        report.append_error(
            f"StepGetVersionsFromCMakeConfigPackageVersion, no matrix config specified, cannot execute step {step.name}"
        )
        return report

    context_os_architecture_compiler_generator = matrix_config.active_os_architecture_compiler_generator
    install_subdir = create_context_os_architecture_compiler_generator_string(
        context_os_architecture_compiler_generator
    )
    input_full_dir = context.base_folder_path / step.base_install_dir / install_subdir
    input_full_path = input_full_dir / Path(step.input_id + ".ver")

    packages = None
    with open(input_full_path) as f:
        line = f.read().strip()
        key, value = line.split("=", 1)
        if key != step.input_dict:
            report.append_error(f"unexpected key {key} in {str(input_full_path)}, expected {step.input_dict}")
            return report
        packages = json.loads(value)

    assert packages is not None

    for item in packages:
        name = item["name"]
        version = item["version"]
        input_path = input_full_dir / Path(name)
        output_path = input_full_dir / Path(name + "-" + version + ".tar.gz")

        report.append_info(f"tar.gz {str(input_path)} to {str(output_path)} ")
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(input_path, arcname=name)

    return report


def step_create_archives_to_githubwf(
    step: StepCreateArchives, wf_job: JobDescription, reporter_sink: ReporterSinkBase
) -> Report:

    install_subdir = step.base_install_dir / create_context_os_architecture_compiler_generator_string_from_components(
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_NAME_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_VERSION_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_ARCHITECTURE_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_ARCHITECTURE_VARIANT_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_COMPILER_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_COMPILER_VERSION_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_GENERATOR_EMBRACED,
    )

    lines = [
        "import json",
        "import os",
        "import tarfile",
        "from pathlib import Path",
        "",
        "versions = json.loads(os.environ['VERSIONS'])",
        "",
        "for entry in versions:",
        "    name = entry['name']",
        "    version = entry['version']",
        f"    input_path = Path('{install_subdir}') / Path(name)",
        f"    output_path = Path('{install_subdir}') / Path(name + '-' + version + '.tar.gz')",
        "    ",
        "    with tarfile.open(output_path, 'w:gz') as tar:",
        "      tar.add(input_path, arcname=name)",
    ]

    # produce output
    run_str_list = ["|"] + lines

    wf_job.steps.append(
        StepRunCommand(
            name="Create Archives",
            shell_type="python",
            env=[f"VERSIONS: ${{{{ steps.{step.input_id}.outputs.{step.input_dict} }}}}"],
            run=run_str_list,
        )
    )

    return Report()


def validate_step_create_archives(step: StepCreateArchives) -> Report:
    report = Report()
    return report
