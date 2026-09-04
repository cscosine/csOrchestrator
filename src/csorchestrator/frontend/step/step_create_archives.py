import inspect
import tarfile
from dataclasses import dataclass
from pathlib import Path

from csorchestrator.domain.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string,
)
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import StepBase
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.github_workflow_translation.github_step_interface import GithubStepInterface
from csorchestrator.frontend.github_workflow_translation.github_workflow_matrix_constants import (
    create_context_os_architecture_compiler_generator_string_github_matrix,
)
from csorchestrator.frontend.github_workflow_translation.github_workflow_steps_transations import StepRunCommand
from csorchestrator.frontend.github_workflow_translation.matrix_execution_context import (
    JobOrchestratorMatrixExecutionContext,
)
from csorchestrator.frontend.github_workflow_translation.orchestrator_visitor_github_wf_generator import (
    OptionalListGithubStepsWithReport,
    StepCapabilityGithubWorkflow,
)
from csorchestrator.frontend.local_execution.context_local_execution import (
    ContextLocalExecution,
)
from csorchestrator.frontend.local_execution.orchestrator_visitor_local_executor import StepCapabilityLocalExecution
from csorchestrator.frontend.step.step_get_versions_from_cmake_config_package_version import (
    create_version_file_name,
)
from csorchestrator.portable.package_version import PackageVersion
from csorchestrator.portable.release_manifest import ReleaseManifest


@dataclass
class StepCreateArchivesCapabilityGithubWorkflow(StepCapabilityGithubWorkflow):
    step: "StepCreateArchives"

    def to_githubwf(
        self, wf_job: JobOrchestratorMatrixExecutionContext, reporter_sink: ReporterSinkBase
    ) -> OptionalListGithubStepsWithReport:
        return step_create_archives_to_githubwf(self.step, wf_job, reporter_sink)


@dataclass
class StepCreateArchivesCapabilityLocalExecution(StepCapabilityLocalExecution):
    step: "StepCreateArchives"

    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_create_archives(self.step, context, reporter_sink)


@dataclass
class StepCreateArchives(StepBase):
    base_install_dir: Path

    def __post_init__(self) -> None:
        self.add_capability(StepCreateArchivesCapabilityGithubWorkflow(self), StepCapabilityGithubWorkflow)
        self.add_capability(StepCreateArchivesCapabilityLocalExecution(self), StepCapabilityLocalExecution)


# TODO: minimze code repetition between local execution and github wf


def execute_step_create_archives(
    step: StepCreateArchives, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    install_subdir = create_context_os_architecture_compiler_generator_string(
        context.get_active_os_architecture_compiler_generator()
    )
    input_base_dir = Path(context.base_folder_path / step.base_install_dir).resolve()
    input_full_path = Path(
        input_base_dir
        / Path(create_version_file_name(context.orchestrator_description.name_and_version_string, install_subdir))
    ).resolve()

    # load which packages to create archives for from the version file (eg. eigen3: 3.4.0, boost: 1.82.0, etc)
    packages = ReleaseManifest.load_release_manifest(input_full_path)
    if len(packages.variants) == 0 or len(packages.variants) > 1:
        report.append_error(
            f"release manifest {str(input_full_path)} has {len(packages.variants)} variants, expected 1"
        )
        return report

    context_os_architecture_compiler_generator_string = create_context_os_architecture_compiler_generator_string(
        context.get_active_os_architecture_compiler_generator()
    )

    if context_os_architecture_compiler_generator_string != packages.variants[0].variant:
        report.append_error(
            f"release manifest {str(input_full_path)} has variant name {packages.variants[0].variant}, expected {context_os_architecture_compiler_generator_string}"  # noqa: E501
        )
        return report

    for item in packages.variants[0].entries:
        input_path = Path(input_base_dir / install_subdir / Path(item.name)).resolve()
        output_path = Path(
            input_base_dir / Path(str(install_subdir) + "-" + item.name + "-" + item.version + ".tar.gz")
        ).resolve()

        report.append_info(f"tar.gz {str(input_path)} to {str(output_path)} ")
        with tarfile.open(output_path, "w:gz") as tar:
            for path in input_path.rglob("*"):
                resolved_path = path.resolve()
                arcname = path.resolve().relative_to(input_base_dir)
                tar.add(resolved_path, arcname=arcname)

    return report


def step_create_archives_to_githubwf(
    step: StepCreateArchives, wf_job: JobOrchestratorMatrixExecutionContext, reporter_sink: ReporterSinkBase
) -> OptionalListGithubStepsWithReport:

    install_dir_name = create_context_os_architecture_compiler_generator_string_github_matrix()
    install_subdir = step.base_install_dir / install_dir_name
    input_full_path = Path(
        step.base_install_dir
        / Path(create_version_file_name(wf_job.orchestrator_description.name_and_version_string, install_dir_name))
    )

    lines = [
        "import json",
        "import os",
        "import sys",
        "import tarfile",
        "from dataclasses import dataclass",
        "from pathlib import Path",
        "",
    ]

    lines += inspect.getsource(PackageVersion).splitlines()
    lines += [""]

    lines += [
        "",
        f"packages = load_version_file('{input_full_path}')",
        "",
        "if packages is None:",
        "    sys.exit('packages was not loaded')",
        "",
        "for item in packages:",
        f"    install_subdir = Path('{install_subdir.as_posix()}').resolve()",
        "    source_path = Path(install_subdir / Path(item.name)).resolve()",
        f"    output_path = Path(install_subdir / Path('{install_dir_name}' + '-' + item.name + '-' + item.version + '.tar.gz')).resolve()",  # noqa: E501
        "",
        "    with tarfile.open(output_path, 'w:gz') as tar:",
        "        for path in source_path.rglob('*'):",
        "            resolved_path = path.resolve()",
        "            arcname = path.resolve().relative_to(install_subdir)",
        "            tar.add(resolved_path, arcname=arcname)",
    ]

    # produce output

    steps: list[GithubStepInterface] = [
        StepRunCommand(
            name="Create Archives",
            shell_type="python",
            run=lines,
        )
    ]

    return OptionalListGithubStepsWithReport.createResultAndReport(steps, Report())
