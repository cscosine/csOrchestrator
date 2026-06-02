import inspect
import json
import re
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
from csorchestrator.core.expected import Expected
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase


@dataclass(frozen=True)
class CMakeConfigPackageVersionGrep:
    name: str
    version_file: Path
    base_install_dir: Path


@dataclass
class StepGetVersionsFromCMakeConfigPackageVersion(StepBase):
    repos: list[CMakeConfigPackageVersionGrep]
    id: str
    output_dict_name: str


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

    result = []
    for repo in step.repos:
        target_full_path: Path = context.base_folder_path / repo.base_install_dir / install_subdir / repo.version_file
        version_or_err = grep_package_version_expected(target_full_path)

        if version_or_err.error is not None:
            report.append_error(version_or_err.error)

        else:
            assert version_or_err.value is not None
            version = version_or_err.value
            report.append_info(f"version of {repo.name} is {version}")
            result.append({"name": repo.name, "version": version})

    if report.has_errors():
        return report

    output_file = context.base_folder_path / repo.base_install_dir / install_subdir / Path(step.id + ".ver")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"{step.output_dict_name}={json.dumps(result)}")

    return report


def step_get_versions_from_cmake_config_package_version_to_githubwf(
    step: StepGetVersionsFromCMakeConfigPackageVersion, wf_job: JobDescription, reporter_sink: ReporterSinkBase
) -> Report:
    header = [
        "from pathlib import Path",
        "import re",
        "import json",
        "import sys",
        "import os",
        "",
    ]

    body = inspect.getsource(grep_package_version).splitlines()

    lines = header + body + [""]

    install_subdir = create_context_os_architecture_compiler_generator_string_from_components(
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_NAME_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_VERSION_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_ARCHITECTURE_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_ARCHITECTURE_VARIANT_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_COMPILER_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_COMPILER_VERSION_EMBRACED,
        MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_GENERATOR_EMBRACED,
    )

    lines += ["files = {"]
    for repo in step.repos:
        target_full_path: Path = repo.base_install_dir / install_subdir / repo.version_file
        lines += ['    "' + repo.name + '": "' + str(target_full_path) + '",']
    lines += ["}", ""]

    lines += ["result = []"]
    lines += ["for name, filename in files.items():"]
    lines += ["  version_or_err = grep_package_version(filename)"]
    lines += ["  v_or_err = grep_package_version(filename=filename)"]
    lines += ["  if v_or_err[0] is not None:"]
    lines += ["      version = v_or_err[0]"]
    lines += ["      result.append({'name': name,'version': version})"]
    lines += ["  elif v_or_err[1] is not None:"]
    lines += ["      sys.exit(f'ERROR: processing {name} at {filename}: {v_or_err[1]}')"]
    lines += ["  else:"]
    lines += ["      sys.exit('ERROR: unexpected behavior of grep_package_version processing {name} at {filename}')"]

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
