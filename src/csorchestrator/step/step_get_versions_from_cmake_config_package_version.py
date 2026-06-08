import inspect
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from csorchestrator.ci.github.github_workflow_config import (
    JobOrchestratorMatrixExecution,
    StepRunCommand,
    create_context_os_architecture_compiler_generator_string_github_matrix,
)
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
)
from csorchestrator.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string,
)
from csorchestrator.core.expected import Expected
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase


@dataclass(frozen=True)
class CMakeConfigPackageVersionGrep:
    name: str
    version_file: Path


@dataclass
class StepGetVersionsFromCMakeConfigPackageVersion(StepBase):
    id: str
    output_dict_name: str
    base_install_dir: Path
    repos_config_file_list: list[CMakeConfigPackageVersionGrep] = field(default_factory=list)
    repos_auto_search_list: list[str] = field(default_factory=list)  # name of repos only,
    # will look for {name}-config-version.cmake or {name}ConfigVersion.cmake


# return a tuple bc we do not want dependencies from Expected in github wf
def grep_package_version(filename: Path) -> tuple[str | None, str | None]:
    path = Path(filename)

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


def find_cmake_config_version_expected(search_path: Path, name: str) -> Expected[Path, str]:
    v_or_err = find_cmake_config_version(search_path=search_path, name=name)
    if v_or_err[0] is not None:
        return Expected[Path, str].make_value(v_or_err[0])
    elif v_or_err[1] is not None:
        return Expected[Path, str].make_error(v_or_err[1])
    else:
        return Expected[Path, str].make_error(
            "unexpected behavior of find_cmake_config_version in find_cmake_config_version_expected"
        )


def grep_package_version_expected(filename: Path) -> Expected[str, str]:
    v_or_err = grep_package_version(filename=filename)
    if v_or_err[0] is not None:
        return Expected[str, str].make_value(v_or_err[0])
    elif v_or_err[1] is not None:
        return Expected[str, str].make_error(v_or_err[1])
    else:
        return Expected[str, str].make_error(
            "unexpected behavior of grep_package_version in grep_package_version_expected"
        )


def execute_step_get_versions_from_cmake_config_package_version(
    step: StepGetVersionsFromCMakeConfigPackageVersion, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    install_subdir = create_context_os_architecture_compiler_generator_string(
        context.get_active_os_architecture_compiler_generator()
    )

    result = []
    for repo in step.repos_config_file_list:
        target_full_path: Path = context.base_folder_path / step.base_install_dir / install_subdir / repo.version_file
        version_or_err = grep_package_version_expected(target_full_path)

        if version_or_err.error is not None:
            report.append_error(version_or_err.error)

        else:
            assert version_or_err.value is not None
            version = version_or_err.value
            report.append_info(f"version of {repo.name} is {version}")
            result.append({"name": repo.name, "version": version})

    for name in step.repos_auto_search_list:
        search_path: Path = context.base_folder_path / step.base_install_dir / install_subdir / name
        path_or_err = find_cmake_config_version_expected(search_path=search_path, name=name)
        if path_or_err.error is not None:
            report.append_error(path_or_err.error)

        else:
            assert path_or_err.value is not None
            path = path_or_err.value

            version_or_err = grep_package_version_expected(path)

            if version_or_err.error is not None:
                report.append_error(version_or_err.error)

            else:
                assert version_or_err.value is not None
                version = version_or_err.value
                report.append_info(f"version of {name} is {version} found in {path}")
                result.append({"name": name, "version": version})

    if report.has_errors():
        return report

    output_file = context.base_folder_path / step.base_install_dir / install_subdir / Path(step.id + ".ver")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"{step.output_dict_name}={json.dumps(result)}")

    return report


def step_get_versions_from_cmake_config_package_version_to_githubwf(
    step: StepGetVersionsFromCMakeConfigPackageVersion,
    wf_job: JobOrchestratorMatrixExecution,
    reporter_sink: ReporterSinkBase,
) -> Report:
    header = [
        "from pathlib import Path",
        "import re",
        "import json",
        "import sys",
        "import os",
        "",
    ]

    body1 = inspect.getsource(grep_package_version).splitlines()
    body2 = inspect.getsource(find_cmake_config_version).splitlines()

    lines = header + body1 + [""] + body2 + [""]

    install_subdir = create_context_os_architecture_compiler_generator_string_github_matrix()

    lines += ["files = {"]
    for repo in step.repos_config_file_list:
        target_full_path: Path = step.base_install_dir / install_subdir / repo.version_file
        lines += ['    "' + repo.name + '": "' + str(target_full_path) + '",']
    lines += ["}", ""]

    lines += ["result = []"]
    lines += ["for name, filename in files.items():"]
    lines += ["  v_or_err = grep_package_version(filename=filename)"]
    lines += ["  if v_or_err[0] is not None:"]
    lines += ["      version = v_or_err[0]"]
    lines += ["      result.append({'name': name,'version': version})"]
    lines += ["  elif v_or_err[1] is not None:"]
    lines += ["      sys.exit(f'ERROR: processing {name} at {filename}: {v_or_err[1]}')"]
    lines += ["  else:"]
    lines += ["      sys.exit('ERROR: unexpected behavior of grep_package_version processing {name} at {filename}')"]
    lines += [""]

    lines += ["repos_auto_search_list = ["]
    for name in step.repos_auto_search_list:
        lines += ['    "' + name + '",']
    lines += ["]", ""]

    search_path_base = step.base_install_dir / install_subdir
    lines += ["for name in repos_auto_search_list:"]
    lines += [f"  search_path: Path = Path('{search_path_base.as_posix()}') / name"]
    lines += ["  path_or_err = find_cmake_config_version(search_path=search_path, name=name)"]
    lines += ["  if path_or_err[0] is not None:"]
    lines += ["    path = path_or_err[0]"]
    lines += ["    v_or_err = grep_package_version(filename=path)"]
    lines += ["    if v_or_err[0] is not None:"]
    lines += ["      version = v_or_err[0]"]
    lines += ["      result.append({'name': name,'version': version})"]
    lines += ["    elif v_or_err[1] is not None:"]
    lines += ["      sys.exit(f'ERROR: processing {name} at {filename}: {v_or_err[1]}')"]
    lines += ["    else:"]
    lines += ["      sys.exit('ERROR: unexpected behavior of grep_package_version processing {name} at {filename}')"]
    lines += ["  elif path_or_err[1] is not None:"]
    lines += ["      sys.exit(f'ERROR: processing {name} : {path_or_err[1]}')"]
    lines += ["  else:"]
    lines += ["      sys.exit('ERROR: unexpected behavior of find_cmake_config_version processing {name}')"]
    lines += [""]

    lines += [""]
    lines += ['output_file = os.environ["GITHUB_OUTPUT"]']
    lines += ['with open(output_file, "w", encoding="utf-8") as f:']
    lines += [f'    f.write(f"{step.output_dict_name}={{json.dumps(result)}}")']
    lines += [""]

    # produce output
    run_str_list = [
        "|",
    ] + lines

    wf_job.steps.append(
        StepRunCommand(
            name="Get Versions",
            id=step.id,
            shell_type="python",
            run=run_str_list,
        )
    )

    return Report()


def validate_step_get_versions_from_cmake_config_package_version(
    step: StepGetVersionsFromCMakeConfigPackageVersion,
) -> Report:
    report = Report()
    return report
