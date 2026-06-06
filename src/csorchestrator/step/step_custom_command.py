import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, TextIO

from csorchestrator.ci.github.github_workflow_config import (
    JobOrchestratorMatrixExecution,
    MatrixOsArchCompilerGeneratorRunnerEntryInclude,
    StepRunCommand,
)
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
)
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.step.step_utils import StepExecuteOnlyOn


@dataclass(kw_only=True)
class StepBashScriptCommand(StepBase):
    cmd: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class StepWinPSCommand(StepBase):
    cmd: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class StepInstallAptPackages(StepBashScriptCommand):
    packages: list[str]

    def __post_init__(self) -> None:
        script = [
            "set -euo pipefail # enable strict mode",
            "",
            "if [ -t 0 ]; then",
            "    # if running in interactive terminal, ask for password if needed",
            '    SUDO="sudo"',
            "else",
            "    # if running in a non-interactive terminal (e.g. in CI workflows), use sudo without ",
            "    #   password prompt (fail if password is needed)",
            '    SUDO="sudo -n"',
            "fi",
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


def execute_step_custom_command(
    step: StepBashScriptCommand, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    errors = execute_command(["bash", "-c", "\n".join(step.cmd)], context.base_folder_path, reporter_sink)
    for e in errors:
        report.append_error(e)

    return report


def get_if_str(step: StepBase) -> str | None:
    if step.get_extra(StepExecuteOnlyOn) is not None:
        execute_only_on_extra = step.get_extra(StepExecuteOnlyOn)
        if execute_only_on_extra is not None:
            os_str = execute_only_on_extra.os.value.lower()
            if execute_only_on_extra.version_starts_with is not None:
                # if: ${{ matrix.os == 'linux' && startsWith(matrix.os, 'ubuntu') }}
                if_str = f"${{{{ {MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_NAME} == '{os_str}' && startsWith({MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_VERSION}, '{execute_only_on_extra.version_starts_with}') }}}}"  # noqa: E501
            else:
                if_str = f"${{{{ {MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_NAME} == '{os_str}' }}}}"
            return if_str
    return None


def step_custom_command_to_githubwf(
    step: StepBashScriptCommand, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:

    run_str_list = ["|"]
    run_str_list += step.cmd

    wf_job.steps.append(
        StepRunCommand(
            name=f"Run command {step.name}",
            if_str=get_if_str(step),
            shell_type="bash",
            run=run_str_list,
        )
    )

    return Report()


def validate_step_custom_command(step: StepBashScriptCommand) -> Report:
    report = Report()
    return report


# ------------------------------


def execute_step_win_ps_command(
    step: StepWinPSCommand, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    errors = execute_command(["powershell", "-Command", "; ".join(step.cmd)], context.base_folder_path, reporter_sink)
    for e in errors:
        report.append_error(e)

    return report


def step_win_ps_command_to_githubwf(
    step: StepWinPSCommand, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:

    run_str_list = ["|"]
    run_str_list += step.cmd

    wf_job.steps.append(
        StepRunCommand(
            name=f"Run command {step.name}",
            if_str=get_if_str(step),
            shell_type="powershell",
            run=run_str_list,
        )
    )

    return Report()


def validate_step_win_ps_command(step: StepWinPSCommand) -> Report:
    report = Report()
    return report
