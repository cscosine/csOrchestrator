import inspect
from dataclasses import dataclass
from pathlib import Path

from csorchestrator.domain.context.context_os_architecture_compiler_generator import (
    ContextOsArchitectureCompilerGenerator,
    create_context_os_architecture_compiler_generator_string,
)
from csorchestrator.domain.orchestrator.workflow_config import (
    ReleaseCreationOnTagConfigBase,
)
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.github_workflow_translation.github_workflow_job_create_release import (
    ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow,
)
from csorchestrator.frontend.github_workflow_translation.github_workflow_steps_transations import StepRunCommand
from csorchestrator.frontend.local_execution.context_local_execution import ContextLocalExecution
from csorchestrator.frontend.local_execution.orchestrator_visitor_local_executor import (
    ReleaseCreationOnTagConfigBaseCapabilityLocalExecution,
)
from csorchestrator.frontend.local_execution.release_creation_context_local_execution import (
    ReleaseCreationContextLocalExecution,
)
from csorchestrator.frontend.release_manifest.manifest import (
    ManifestVersionsEntry,
    create_release_manifest,
    write_release_manifest,
)
from csorchestrator.frontend.step.step_get_versions_from_cmake_config_package_version import (
    CMakeConfigPackageVersion,
    create_version_file_name,
    load_version_file,
)

CS_ORCHESTRATOR_MANIFEST_EXTENSION: str = ".csOrchestratorManifest"


@dataclass
class ReleaseCreationOnTagConfigCapabilityGithubWorkflow(ReleaseCreationOnTagConfigBaseCapabilityGithubWorkflow):
    step: "ReleaseCreationOnTagConfig"

    def to_githubwf_lines(
        self,
        matrix_list: list[ContextOsArchitectureCompilerGenerator],
        name_and_version_string: str,
        artifacts_folder: str,
    ) -> list[str]:
        return release_creation_on_tag_config_to_githubwf(
            self.step, matrix_list, name_and_version_string, artifacts_folder
        )

    def getReleaseFilesExtension(self) -> str | None:
        return CS_ORCHESTRATOR_MANIFEST_EXTENSION


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
    step: ReleaseCreationOnTagConfig,
    matrix_list: list[ContextOsArchitectureCompilerGenerator],
    name_and_version_string: str,
    artifacts_folder: str,
) -> list[str]:
    lines: list[str] = ["|"]

    input_files_list: list[str] = []
    input_names_list: list[str] = []
    for context in matrix_list:
        context_os_architecture_compiler_generator_string = create_context_os_architecture_compiler_generator_string(
            context
        )
        input_names_list.append(context_os_architecture_compiler_generator_string)
        input_files_list.append(
            Path(
                # TODO not nice to use "-" directly here
                Path(name_and_version_string + "-" + context_os_architecture_compiler_generator_string)
                / Path(create_version_file_name(context_os_architecture_compiler_generator_string))
            ).as_posix()
        )

    if len(input_files_list) == 0 or len(input_names_list) == 0:
        return lines

    header = [
        "from dataclasses import dataclass, field",
        "from pathlib import Path",
        "import json",
        "",
    ]
    class1 = inspect.getsource(CMakeConfigPackageVersion).splitlines()
    class2 = inspect.getsource(ManifestVersionsEntry).splitlines()
    fun1 = inspect.getsource(create_release_manifest).splitlines()
    fun2 = inspect.getsource(write_release_manifest).splitlines()
    fun3 = inspect.getsource(load_version_file).splitlines()

    lines += header
    lines += class1
    lines += [""]
    lines += class2
    lines += [""]
    lines += fun1
    lines += [""]
    lines += fun2
    lines += [""]
    lines += fun3
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
    lines += ["release_manifest = create_release_manifest(collected_version_entries)"]
    lines += [f"output_filename = Path('{name_and_version_string}{CS_ORCHESTRATOR_MANIFEST_EXTENSION}')"]
    lines += ["write_release_manifest(release_manifest,output_filename)"]
    lines += [""]

    step_github = StepRunCommand(
        name="Manifest creation", run=lines, shell_type="python", working_directory=artifacts_folder
    )

    return step_github.to_string_lines() + [""]


def release_creation_on_tag_config_execute_local(
    step: ReleaseCreationOnTagConfig, relase_context: ReleaseCreationContextLocalExecution
) -> Report:
    report = Report()

    # first: matrix element string, second packages,version list
    collected_version_entries: list[ManifestVersionsEntry] = []

    counter: int = -1
    for os_architecture_compiler_generator in relase_context.os_architecture_compiler_generator_list:
        counter += 1

        match = os_architecture_compiler_generator.context_os_architecture.can_be_executed_on(
            relase_context.os_architecture
        )
        if not match:
            # TODO introduce a new report section and report skipped
            continue
        # use the compatible os_arcchitecture, not the detected one.
        # e.g. detected os is win 11, but we select win 10 in the matrix, which is compatible

        context = ContextLocalExecution(
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
            input_base_dir / Path(create_version_file_name(context_os_architecture_compiler_generator_string))
        ).resolve()

        packages = load_version_file(input_full_path)
        collected_version_entries.append(
            ManifestVersionsEntry(context_os_architecture_compiler_generator_string, packages)
        )
    release_manifest = create_release_manifest(collected_version_entries)
    output_filename = step.base_install_dir / Path(
        relase_context.name_and_version_string + CS_ORCHESTRATOR_MANIFEST_EXTENSION
    )
    write_release_manifest(
        release_manifest,
        output_filename,
    )

    report.append_info(f"release manifest written to {str(output_filename)}")
    return report
