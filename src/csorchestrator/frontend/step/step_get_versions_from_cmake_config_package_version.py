import inspect
import re
from dataclasses import dataclass, field
from pathlib import Path

from csorchestrator.domain.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string,
)
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import (
    StepBase,
)
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.github_workflow_translation.github_workflow_job_matrix_execution import (
    JobOrchestratorMatrixExecutionContext,
)
from csorchestrator.frontend.github_workflow_translation.github_workflow_matrix_constants import (
    create_context_os_architecture_compiler_generator_string_github_matrix,
)
from csorchestrator.frontend.github_workflow_translation.github_workflow_steps_transations import StepRunCommand
from csorchestrator.frontend.github_workflow_translation.orchestrator_visitor_github_wf_generator import (
    StepCapabilityGithubWorkflow,
)
from csorchestrator.frontend.local_execution.context_local_execution import (
    ContextLocalExecution,
)
from csorchestrator.frontend.local_execution.orchestrator_visitor_local_executor import StepCapabilityLocalExecution
from csorchestrator.portable.package_version import PackageVersion
from csorchestrator.portable.release_manifest import ManifestVersionsEntry, ReleaseManifest


@dataclass(frozen=True)
class CMakeConfigPackageVersionGrep:
    name: str
    version_file: Path


@dataclass
class StepGetVersionsFromCMakeConfigPackageVersionCapabilityGithubWorkflow(StepCapabilityGithubWorkflow):
    step: "StepGetVersionsFromCMakeConfigPackageVersion"

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecutionContext, reporter_sink: ReporterSinkBase) -> Report:
        return step_get_versions_from_cmake_config_package_version_to_githubwf(self.step, wf_job, reporter_sink)


@dataclass
class StepGetVersionsFromCMakeConfigPackageVersionCapabilityLocalExecution(StepCapabilityLocalExecution):
    step: "StepGetVersionsFromCMakeConfigPackageVersion"

    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_get_versions_from_cmake_config_package_version(self.step, context, reporter_sink)


@dataclass
class StepGetVersionsFromCMakeConfigPackageVersion(StepBase):
    base_install_dir: Path
    repos_config_file_list: list[CMakeConfigPackageVersionGrep] = field(default_factory=list)
    repos_auto_search_list: list[str] = field(default_factory=list)  # name of repos only,
    repos_version: list[PackageVersion] = field(default_factory=list)
    # will look for {name}-config-version.cmake or {name}ConfigVersion.cmake

    def __post_init__(self) -> None:
        self.add_capability(
            StepGetVersionsFromCMakeConfigPackageVersionCapabilityGithubWorkflow(self), StepCapabilityGithubWorkflow
        )
        self.add_capability(
            StepGetVersionsFromCMakeConfigPackageVersionCapabilityLocalExecution(self), StepCapabilityLocalExecution
        )


# return a tuple bc we do not want dependencies from Expected in github wf
def grep_package_version(filename: Path) -> tuple[str | None, str | None]:
    path = filename

    if not path.is_file():
        return (None, f"ERROR: file not found: {path}")

    content = path.read_text(encoding="utf-8")

    matches = []

    for m in re.finditer(
        r'set\s*\(\s*PACKAGE_VERSION\s+("([^"]*)"|([^\s\)]+))\s*\)',
        content,
    ):
        value = m.group(2) or m.group(3)

        # Ignore computed values like "${PACKAGE_VERSION} (...)"
        if "${" in value:
            continue

        matches.append(value)

    if len(matches) != 1:
        return (None, f"ERROR: {path}: expected exactly one PACKAGE_VERSION definition, found {len(matches)}")

    version = matches[0]
    return (version, None)


# return a tuple bc we do not want dependencies from Expected in github wf
def find_cmake_config_version(search_path: Path, name: str) -> tuple[Path | None, str | None]:
    candidates = {
        f"{name}-config-version.cmake".lower(),
        f"{name}ConfigVersion.cmake".lower(),
    }

    matches = [p for p in search_path.rglob("*") if p.is_file() and p.name.lower() in candidates]

    if not matches:
        return (None, f"No config version file found for '{name}' under '{search_path}'")

    if len(matches) > 1:
        return (None, "Multiple config version files found:" + ", ".join(str(p) for p in matches))

    return (matches[0], None)


@dataclass
class VersionSearchOutput:
    versions: list[PackageVersion] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def get_versions_helper(
    repos_config_file_list: list[CMakeConfigPackageVersionGrep],  # pairs of repo and files reporting versions
    repos_auto_search_list: list[str],  # repo name only
    repos_version: list[PackageVersion],  # pairs of repo and versions
    base_install_dir: Path,
    install_subdir: Path,
    base_folder_path: Path | None,
) -> VersionSearchOutput:
    result = VersionSearchOutput()

    # fixed versions
    for repo_v in repos_version:
        result.versions.append(PackageVersion(name=repo_v.name, version=repo_v.version))

    # repo with version with file hint
    for repo in repos_config_file_list:
        if base_folder_path is not None:
            target_full_path = base_folder_path / base_install_dir / install_subdir / repo.version_file
        else:
            target_full_path = base_install_dir / install_subdir / repo.version_file

        version_or_err = grep_package_version(target_full_path)

        if version_or_err[1] is not None:
            result.errors.append(version_or_err[1])

        else:
            assert version_or_err[0] is not None
            version = version_or_err[0]
            result.versions.append(PackageVersion(name=repo.name, version=version))

    # repo with version autosearch
    for name in repos_auto_search_list:
        if base_folder_path is not None:
            search_path = base_folder_path / base_install_dir / install_subdir / name
        else:
            search_path = base_install_dir / install_subdir / name
        path_or_err = find_cmake_config_version(search_path=search_path, name=name)
        if path_or_err[1] is not None:
            result.errors.append(path_or_err[1])

        else:
            assert path_or_err[0] is not None
            path = path_or_err[0]

            version_or_err = grep_package_version(path)

            if version_or_err[1] is not None:
                result.errors.append(version_or_err[1])

            else:
                assert version_or_err[0] is not None
                version = version_or_err[0]
                result.versions.append(PackageVersion(name=name, version=version))

    return result


def create_version_file_name(
    orchestrator_name_and_version_string: str, context_os_architecture_compiler_generator_string: str
) -> str:
    return (
        orchestrator_name_and_version_string
        + "-"
        + context_os_architecture_compiler_generator_string
        + ReleaseManifest.CS_ORCHESTRATOR_MANIFEST_EXTENSION
    )


def execute_step_get_versions_from_cmake_config_package_version(
    step: StepGetVersionsFromCMakeConfigPackageVersion, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    context_os_architecture_compiler_generator_string = create_context_os_architecture_compiler_generator_string(
        context.get_active_os_architecture_compiler_generator()
    )

    result = get_versions_helper(
        step.repos_config_file_list,
        step.repos_auto_search_list,
        step.repos_version,
        step.base_install_dir,
        Path(context_os_architecture_compiler_generator_string),
        context.base_folder_path,
    )

    if len(result.errors) > 0:
        for e in result.errors:
            report.append_error(e)
        return report

    for p in result.versions:
        report.append_info(f"repo: {p.name} version: {p.version}")

    output_file = (
        context.base_folder_path
        / step.base_install_dir
        / Path(
            create_version_file_name(
                context.orchestrator_description.name_and_version_string,
                context_os_architecture_compiler_generator_string,
            )
        )
    )

    entry = ManifestVersionsEntry(variant=context_os_architecture_compiler_generator_string, entries=result.versions)
    manifest = ReleaseManifest(
        project_name=context.orchestrator_description.orchestrator_name,
        project_version=context.orchestrator_description.orchestrator_version,
        variants=[entry],
    )

    manifest.write_release_manifest(output_file)

    return report


def _create_python_list_string(src_list: list[str], list_name: str) -> list[str]:
    lines: list[str] = []
    if len(src_list) == 0:
        lines += [f"{list_name} : list[str] = []", ""]
    else:
        lines += [f"{list_name} : list[str] = ["]
        for r2 in src_list:
            lines += [f"    '{r2}',"]
        lines += ["]", ""]
    return lines


def _create_python_list_class_grep(src_list: list[CMakeConfigPackageVersionGrep], list_name: str) -> list[str]:
    lines: list[str] = []
    if len(src_list) == 0:
        lines += [f"{list_name} : list[CMakeConfigPackageVersionGrep] = []", ""]
    else:
        lines += [f"{list_name} : list[CMakeConfigPackageVersionGrep] = ["]
        for r1 in src_list:
            lines += [f"    CMakeConfigPackageVersionGrep('{r1.name}', Path('{r1.version_file}')),"]
        lines += ["]", ""]
    return lines


def _create_python_list_class_version(src_list: list[PackageVersion], list_name: str) -> list[str]:
    lines: list[str] = []
    if len(src_list) == 0:
        lines += [f"{list_name}: list[CMakeConfigPackageVersion] = []", ""]
    else:
        lines += [f"{list_name}: list[CMakeConfigPackageVersion] = ["]
        for r3 in src_list:
            lines += [f"    CMakeConfigPackageVersion('{r3.name}', '{r3.version}'),"]
        lines += ["]", ""]
    return lines


# TODO: minimze code repetition between local execution and github wf


def step_get_versions_from_cmake_config_package_version_to_githubwf(
    step: StepGetVersionsFromCMakeConfigPackageVersion,
    wf_job: JobOrchestratorMatrixExecutionContext,
    reporter_sink: ReporterSinkBase,
) -> Report:
    header = [
        "from pathlib import Path",
        "import re",
        "import json",
        "import sys",
        "import os",
        "from dataclasses import dataclass, field, asdict",
        "from typing import Any, ClassVar",
        "",
    ]
    class1 = inspect.getsource(CMakeConfigPackageVersionGrep).splitlines()
    class2 = inspect.getsource(PackageVersion).splitlines()
    class3 = inspect.getsource(VersionSearchOutput).splitlines()
    body1 = inspect.getsource(grep_package_version).splitlines()
    body2 = inspect.getsource(find_cmake_config_version).splitlines()
    body3 = inspect.getsource(get_versions_helper).splitlines()

    lines = header + class1 + [""] + class2 + [""] + class3 + [""] + body1 + [""] + body2 + [""] + body3 + [""]

    install_subdir = create_context_os_architecture_compiler_generator_string_github_matrix()

    lines += _create_python_list_class_grep(step.repos_config_file_list, "repos_config_file_list")
    lines += _create_python_list_string(step.repos_auto_search_list, "repos_auto_search_list")
    lines += _create_python_list_class_version(step.repos_version, "repos_version")

    lines += [
        "result = get_versions_helper(",
        "    repos_config_file_list,",
        "    repos_auto_search_list,",
        "    repos_version,",
        f"    Path('{step.base_install_dir}'),",
        f"    Path('{install_subdir}'),",
        "    None",
        ")",
    ]

    lines += [
        "if len(result.errors) > 0:",
        "    for e in result.errors:",
        "        print(e)",
        "    sys.exit('ERROR: getting package versions')",
    ]
    lines += [""]

    lines += [
        "output_file = (",
        f"    Path('{step.base_install_dir}')",
        f"    / Path('{create_version_file_name(wf_job.orchestrator_description.name_and_version_string, install_subdir)}')",  # noqa: E501
    ]
    lines += [")", ""]
    lines += ["write_version_file(output_file, result.versions)"]
    lines += [""]

    # produce output

    wf_job.job.steps.append(
        StepRunCommand(
            name="Get Versions",
            shell_type="python",
            run=lines,
        )
    )

    return Report()
