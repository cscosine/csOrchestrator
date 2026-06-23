import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path
from string import Template
from typing import Callable, TextIO

from csorchestrator.ci.github.github_workflow_steps_transations import StepRunCommand
from csorchestrator.ci.github.guthub_workflow_matrix_constants import (
    MatrixOsArchCompilerGeneratorGithubConstants,
    create_context_os_architecture_compiler_generator_string_github_matrix,
)
from csorchestrator.context.context_compiler_generator import (
    GeneratorType,
    get_c_cpp_compiler,
    get_cmake_generator_name,
    get_cmake_toolset,
)
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
)
from csorchestrator.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string,
)
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import (
    JobOrchestratorMatrixExecution,
    StepBase,
    StepValidatorBase,
    StepValidatorNoOp,
)
from csorchestrator.step.step_utils import StepExecuteOnlyOn


@dataclass(kw_only=True)
class StepBashScriptCommand(StepBase):
    cmd: list[str] = field(default_factory=list)
    dry_run: bool = False

    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_custom_command(self, context, reporter_sink)

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return step_custom_command_to_githubwf(self, wf_job, reporter_sink)

    @classmethod
    def createValidator(cls) -> StepValidatorBase:
        return StepValidatorNoOp()


@dataclass(kw_only=True)
class StepWinPSCommand(StepBase):
    cmd: list[str] = field(default_factory=list)
    dry_run: bool = False

    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_win_ps_command(self, context, reporter_sink)

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return step_win_ps_command_to_githubwf(self, wf_job, reporter_sink)

    @classmethod
    def createValidator(cls) -> StepValidatorBase:
        return StepValidatorNoOp()


@dataclass(kw_only=True)
class StepInstallAptPackages(StepBashScriptCommand):
    packages: list[str]

    def __post_init__(self) -> None:
        script = [
            "set -euo pipefail # enable strict mode",
            "",
            "",
            "packages=(",
        ]
        script += [f"  {p}" for p in self.packages]
        script += [
            ")",
            "",
            "missing=()",
            "",
            'for pkg in "${packages[@]}"; do',
            '  dpkg -s "$pkg" &>/dev/null || missing+=("$pkg")',
            "done",
            "",
            "if [ ${#missing[@]} -ne 0 ]; then",
            "",
            "  sudo apt update",
            "",
            '  echo "Need to install missing packages: ${missing[*]}"',
            '  sudo apt install -y "${missing[@]}"',
            "else",
            '  echo "All packages already installed."',
            "fi",
        ]

        self.cmd = script


def execute_command(
    cmd: list[str], working_dir_full_path: Path, reporter_sink: ReporterSinkBase
) -> list[str]:  # return errors, if any

    errors: list[str] = []

    process = subprocess.Popen(
        cmd,
        cwd=str(working_dir_full_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    def stream(
        pipe: TextIO,
        sink_func: Callable[[str], None],
    ) -> None:
        try:
            for line in iter(pipe.readline, ""):
                if line:
                    sink_func(line.rstrip("\n"))
        finally:
            pipe.close()

    stdout_thread = threading.Thread(
        target=stream,
        args=(process.stdout, reporter_sink.stdout),
        daemon=True,
    )

    stderr_thread = threading.Thread(
        target=stream,
        args=(process.stderr, reporter_sink.stderr),
        daemon=True,
    )

    stdout_thread.start()
    stderr_thread.start()

    try:
        return_code = process.wait()
    except Exception as e:
        process.kill()
        errors += [f"Failed to run cmake workflow: {e}"]
        # do not return, attempt to close threads

    stdout_thread.join()
    stderr_thread.join()

    if return_code != 0:
        errors += [f"Command failed with exit code {return_code}"]
        # do not return immediately, do at cycle end

    return errors


def evaluate_cmd_variable_subst_local(cmd: list[str], context: ContextLocalExecution) -> list[str]:
    c_cpp_compiler = get_c_cpp_compiler(context.active_compiler_generator.compiler_family)
    toolset = get_cmake_toolset(context.active_compiler_generator.compiler_family)

    subst: dict[str, str] = {
        "CS_DIR_FROM_MATRIX": create_context_os_architecture_compiler_generator_string(
            context.get_active_os_architecture_compiler_generator()
        ),
        # variables
        "CS_MATRIX_EXEC_ID": str(context.matrix_execution_id),
        "CS_OS": context.os_architecture.os.value.lower(),
        "CS_OS_VERSION": context.os_architecture.os_version.lower(),
        "CS_ARCHITECTURE": context.os_architecture.architecture.value.lower(),
        "CS_ARCHITECTURE_VARIANT": context.os_architecture.architecture_variant.lower(),
        "CS_COMPILER_FAMILY": context.active_compiler_generator.compiler_family.value.lower(),
        "CS_COMPILER_VERSION": context.active_compiler_generator.compiler_version.lower(),
        "CS_GENERATOR": context.active_compiler_generator.build_generator.generator.value.lower(),
        "CS_GENERATOR_TYPE": context.active_compiler_generator.build_generator.generator_type.value.lower(),
        "CS_GENERATOR_TYPE_SINGLECONFIG": GeneratorType.SINGLE_CONFIG.value,
        "CS_GENERATOR_TYPE_MULTICONFIG": GeneratorType.MULTI_CONFIG.value,
        "CS_GENERATOR_CMAKE": get_cmake_generator_name(context.active_compiler_generator.build_generator.generator)
        or "",
        "CS_C_COMPILER": c_cpp_compiler[0] or "",
        "CS_CPP_COMPILER": c_cpp_compiler[1] or "",
        "CS_TOOLSET": toolset or "",
    }
    subst_cmd = [Template(c).safe_substitute(subst) for c in cmd]
    return subst_cmd


def evaluate_cmd_variable_subst_github_wf(cmd: list[str]) -> list[str]:
    subst: dict[str, str] = {
        "CS_DIR_FROM_MATRIX": create_context_os_architecture_compiler_generator_string_github_matrix(),
        "CS_MATRIX_EXEC_ID": MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_EXECUTION_ID_EMBRACED,
        "CS_OS": MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_OS_NAME_EMBRACED,
        "CS_OS_VERSION": MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_OS_VERSION_EMBRACED,
        "CS_ARCHITECTURE": MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_ARCHITECTURE_EMBRACED,
        "CS_ARCHITECTURE_VARIANT": MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_ARCHITECTURE_VARIANT_EMBRACED,
        "CS_COMPILER_FAMILY": MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_COMPILER_EMBRACED,
        "CS_COMPILER_VERSION": MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_COMPILER_VERSION_EMBRACED,
        "CS_GENERATOR": MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_GENERATOR_EMBRACED,
        "CS_GENERATOR_TYPE": MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_GENERATOR_TYPE_EMBRACED,
        "CS_GENERATOR_TYPE_SINGLECONFIG": GeneratorType.SINGLE_CONFIG.value,
        "CS_GENERATOR_TYPE_MULTICONFIG": GeneratorType.MULTI_CONFIG.value,
        "CS_GENERATOR_CMAKE": MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_GENERATOR_CMAKE_EMBRACED,
        "CS_C_COMPILER": MatrixOsArchCompilerGeneratorGithubConstants.C_COMPILER_EMBRACED,
        "CS_CPP_COMPILER": MatrixOsArchCompilerGeneratorGithubConstants.CPP_COMPILER_EMBRACED,
        "CS_TOOLSET": MatrixOsArchCompilerGeneratorGithubConstants.TOOLSET_EMBRACED,
    }
    subst_cmd = []
    for c in cmd:
        print(c)
        cc = Template(c).safe_substitute(subst)
        print(cc)

        subst_cmd += [cc]

    return subst_cmd


def execute_step_custom_command(
    step: StepBashScriptCommand, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    cmd_evaluated = evaluate_cmd_variable_subst_local(step.cmd, context)
    cmd_string = ["bash", "-c", "\n".join(cmd_evaluated)]

    reporter_sink.stdout("\n".join(cmd_string))
    if not step.dry_run:
        errors = execute_command(cmd_string, context.base_folder_path, reporter_sink)
        for e in errors:
            report.append_error(e)

    return report


def get_if_str(step: StepBase) -> str | None:
    if step.get_extra(StepExecuteOnlyOn) is not None:
        execute_only_on_extra = step.get_extra(StepExecuteOnlyOn)
        if execute_only_on_extra is not None:
            os_str = execute_only_on_extra.os.value.lower()
            if execute_only_on_extra.version_starts_with is not None:
                if_str = f"${{{{ {MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_OS_NAME} == '{os_str}' && startsWith({MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_OS_VERSION}, '{execute_only_on_extra.version_starts_with}') }}}}"  # noqa: E501
            else:
                if_str = f"${{{{ {MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_OS_NAME} == '{os_str}' }}}}"
            return if_str
    return None


def step_custom_command_to_githubwf(
    step: StepBashScriptCommand, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:

    cmd_evaluated = evaluate_cmd_variable_subst_github_wf(step.cmd)

    run_str_list = ["|"]
    run_str_list += cmd_evaluated

    wf_job.steps.append(
        StepRunCommand(
            name=f"Run command {step.name}",
            if_str=get_if_str(step),
            shell_type="bash",
            run=run_str_list,
        )
    )

    return Report()


# ------------------------------


def execute_step_win_ps_command(
    step: StepWinPSCommand, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    cmd_evaluated = evaluate_cmd_variable_subst_local(step.cmd, context)
    cmd_string = ["powershell", "-Command", "; ".join(cmd_evaluated)]

    reporter_sink.stdout("\n".join(cmd_string))
    if not step.dry_run:
        errors = execute_command(cmd_string, context.base_folder_path, reporter_sink)
        for e in errors:
            report.append_error(e)

    return report


def step_win_ps_command_to_githubwf(
    step: StepWinPSCommand, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:

    cmd_evaluated = evaluate_cmd_variable_subst_github_wf(step.cmd)

    run_str_list = ["|"]
    run_str_list += cmd_evaluated

    wf_job.steps.append(
        StepRunCommand(
            name=f"Run command {step.name}",
            if_str=get_if_str(step),
            shell_type="powershell",
            run=run_str_list,
        )
    )

    return Report()
