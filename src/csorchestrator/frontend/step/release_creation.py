import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from csorchestrator.domain.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string,
)
from csorchestrator.domain.orchestrator.workflow_config import (
    ReleaseCreationOnTagConfigBase,
)
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.github_workflow_translation.github_workflow_job_create_release import (
    ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow,
)
from csorchestrator.frontend.github_workflow_translation.github_workflow_steps_translations import StepRunCommand
from csorchestrator.frontend.github_workflow_translation.release_creation_context import ReleaseCreationContext
from csorchestrator.frontend.local_execution.context_local_execution import ContextLocalExecution
from csorchestrator.frontend.local_execution.orchestrator_visitor_local_executor import (
    ReleaseCreationOnTagConfigBaseCapabilityLocalExecution,
)
from csorchestrator.frontend.local_execution.release_creation_context_local_execution import (
    ReleaseCreationContextLocalExecution,
)
from csorchestrator.frontend.local_execution.validate_and_execute import create_context_os_architecture_string
from csorchestrator.frontend.step.step_get_versions_from_cmake_config_package_version import (
    create_version_file_name,
)
from csorchestrator.portable.package_version import PackageVersion
from csorchestrator.portable.release_manifest import (
    ManifestVersionsEntry,
    ReleaseManifest,
)


@dataclass
class ReleaseCreationOnTagConfigCapabilityGithubWorkflow(ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow):
    step: "ReleaseCreationOnTagConfig"

    def to_steps_dict(self, release_creation_context: ReleaseCreationContext) -> list[dict[str, Any]]:
        return release_creation_on_tag_config_to_githubwf(self.step, release_creation_context)


@dataclass
class ReleaseCreationOnTagConfiCapabilityLocalExecution(ReleaseCreationOnTagConfigBaseCapabilityLocalExecution):
    step: "ReleaseCreationOnTagConfig"

    def execute_locally(self, context: ReleaseCreationContextLocalExecution) -> Report:
        return release_creation_on_tag_config_execute_local(self.step, context)


@dataclass
class ReleaseCreationOnTagConfig(ReleaseCreationOnTagConfigBase):
    base_install_dir: Path  # used only in local executions, not in github wf where artifacts are downloaded

    def __post_init__(self) -> None:
        self.add_capability(
            ReleaseCreationOnTagConfigCapabilityGithubWorkflow(self),
            ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow,
        )
        self.add_capability(
            ReleaseCreationOnTagConfiCapabilityLocalExecution(self),
            ReleaseCreationOnTagConfigBaseCapabilityLocalExecution,
        )


def release_creation_on_tag_config_to_githubwf(
    step: ReleaseCreationOnTagConfig, release_creation_context: ReleaseCreationContext
) -> list[dict[str, Any]]:

    input_files_list: list[str] = []
    input_names_list: list[str] = []
    for context in release_creation_context.matrix_list:
        context_os_architecture_compiler_generator_string = create_context_os_architecture_compiler_generator_string(
            context
        )
        input_names_list.append(context_os_architecture_compiler_generator_string)
        input_files_list.append(
            Path(
                Path(
                    release_creation_context.orchestrator_description.name_and_version_string
                    + "-"
                    + context_os_architecture_compiler_generator_string
                )
                / Path(
                    create_version_file_name(
                        release_creation_context.orchestrator_description.name_and_version_string,
                        context_os_architecture_compiler_generator_string,
                    )
                )
            ).as_posix()
        )

    if len(input_files_list) == 0 or len(input_names_list) == 0:
        return []

    lines: list[str] = []

    header = [
        "from dataclasses import dataclass, field, asdict",
        "from typing import Any, ClassVar",
        "from pathlib import Path",
        "import json",
        "",
    ]
    class1 = inspect.getsource(PackageVersion).splitlines()
    class2 = inspect.getsource(ManifestVersionsEntry).splitlines()
    class3 = inspect.getsource(ReleaseManifest).splitlines()

    lines += header
    lines += class1
    lines += [""]
    lines += class2
    lines += [""]
    lines += class3
    lines += [""]

    lines += ["input_files_list = ["]
    lines += [f"  '{x}'," for x in input_files_list]
    lines += ["]"]
    lines += [""]
    lines += ["input_names_list = ["]
    lines += [f"  '{x}'," for x in input_names_list]
    lines += ["]"]
    lines += [""]
    lines += ["collected_version_entries: list[ManifestVersionsEntry] = []"]
    lines += [""]
    lines += ["for name,f in zip(input_names_list,input_files_list):"]
    lines += ["  packages = load_version_file(f)"]
    lines += ["  collected_version_entries.append("]
    lines += ["    ManifestVersionsEntry(name, packages)"]
    lines += ["  )"]
    lines += [""]
    lines += ["release_manifest = Manifest("]
    lines += ["  manifest_version=Manifest.MANIFEST_VERSION,"]
    lines += [f"  project_name='{release_creation_context.orchestrator_description.orchestrator_name}',"]
    lines += [f"  project_version='{release_creation_context.orchestrator_description.orchestrator_version}',"]
    lines += ["  variants=collected_version_entries,"]
    lines += [")"]
    lines += [
        f"output_filename = Path('{release_creation_context.orchestrator_description.name_and_version_string}{ReleaseManifest.CS_ORCHESTRATOR_MANIFEST_EXTENSION}')"  # noqa: E501
    ]
    lines += ["release_manifest.write_release_manifest(output_filename)"]
    lines += [""]

    step_github = StepRunCommand(
        name="Manifest creation",
        run=lines,
        shell_type="python",
        working_directory=release_creation_context.artifacts_folder,
    )

    return [
        step_github.to_dict(),
    ]


def release_creation_on_tag_config_execute_local(
    step: ReleaseCreationOnTagConfig, relase_context: ReleaseCreationContextLocalExecution
) -> Report:
    report = Report()

    # first: matrix element string, second packages,version list
    collected_version_entries: list[ManifestVersionsEntry] = []

    for counter, os_architecture_compiler_generator in enumerate(
        relase_context.os_architecture_compiler_generator_list
    ):
        match = os_architecture_compiler_generator.context_os_architecture.can_be_executed_on(
            relase_context.os_architecture
        )
        if not match:
            report.append_info(
                "skip release creation on not compatible matrix config: "
                f"{create_context_os_architecture_compiler_generator_string(os_architecture_compiler_generator)}"
                ", current os and architecture:  "
                f"{create_context_os_architecture_string(relase_context.os_architecture)}"
            )
            continue
        # use the compatible os_arcchitecture, not the detected one.
        # e.g. detected os is win 11, but we select win 10 in the matrix, which is compatible

        context = ContextLocalExecution(
            orchestrator_description=relase_context.orchestrator_description,
            base_folder_path=relase_context.base_path,
            os_architecture=os_architecture_compiler_generator.context_os_architecture,
            active_compiler_generator=os_architecture_compiler_generator.context_compiler_generator,
            matrix_extras={},
            matrix_execution_id=str(counter),
        )

        context_os_architecture_compiler_generator_string = create_context_os_architecture_compiler_generator_string(
            context.get_active_os_architecture_compiler_generator()
        )

        input_base_dir = Path(context.base_folder_path / step.base_install_dir).resolve()
        input_full_path = Path(
            input_base_dir
            / Path(
                create_version_file_name(
                    relase_context.orchestrator_description.name_and_version_string,
                    context_os_architecture_compiler_generator_string,
                )
            )
        ).resolve()

        packages = ReleaseManifest.load_release_manifest(input_full_path)
        if len(packages.variants) == 0 or len(packages.variants) > 1:
            report.append_error(
                f"release manifest {str(input_full_path)} has {len(packages.variants)} variants, expected 1"
            )
            return report

        if context_os_architecture_compiler_generator_string != packages.variants[0].variant:
            report.append_error(
                f"release manifest {str(input_full_path)} has variant name {packages.variants[0].variant}, expected {context_os_architecture_compiler_generator_string}"  # noqa: E501
            )
            return report

        collected_version_entries.append(packages.variants[0])

    release_manifest = ReleaseManifest(
        project_name=relase_context.orchestrator_description.orchestrator_name,
        project_version=relase_context.orchestrator_description.orchestrator_version,
        variants=collected_version_entries,
    )
    output_filename = step.base_install_dir / Path(
        relase_context.orchestrator_description.name_and_version_string
        + ReleaseManifest.CS_ORCHESTRATOR_MANIFEST_EXTENSION
    )
    release_manifest.write_release_manifest(
        output_filename,
    )

    report.append_info(f"release manifest written to {str(output_filename)}")
    return report
