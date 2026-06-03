import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, TextIO

from csorchestrator.ci.github.github_workflow_config import JobOrchestratorMatrixExecution, StepRunCommand
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
    ContextLocalExecutionActiveMatrixConfig,
)
from csorchestrator.context.context_os_architecture_compiler_generator import ContextOsArchitectureCompilerGenerator
from csorchestrator.core.expected import Expected
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase, StepSkipExecutionOnNonMatchingContext


@dataclass(kw_only=True)
class StepCustomCommand(StepBase):
    cmd: list[str] = field(default_factory=list)
    context_os_architecture_compiler_generator: ContextOsArchitectureCompilerGenerator | None = None


@dataclass(kw_only=True)
class StepInstallAptPackages(StepCustomCommand):
    packages: list[str]

    def __post_init__(self) -> None:
        lines = [
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
        lines += self.packages
        lines += [
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

        script = "\n".join(lines)
        self.cmd = ["bash", "-c", script]


# TODO note, in previous impl before sudo apt update
# sudo sed -i 's|mirror+file:/etc/apt/apt-mirrors.txt|http://archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list
# was used only for github actions


def select_execution_context(
    context_os_architecture_compiler_generator: ContextOsArchitectureCompilerGenerator | None,
    matrix_config: ContextLocalExecutionActiveMatrixConfig | None,
) -> Expected[ContextOsArchitectureCompilerGenerator, str]:

    if context_os_architecture_compiler_generator is None:
        # no context, inherit it from the matrix config if any

        if matrix_config is None:
            return Expected[ContextOsArchitectureCompilerGenerator, str].make_error("no matrix config specified")

        context_os_architecture_compiler_generator = matrix_config.active_os_architecture_compiler_generator

    else:
        # has context, use it as a single workflow config step
        pass

    assert context_os_architecture_compiler_generator is not None
    return Expected[ContextOsArchitectureCompilerGenerator, str].make_value(context_os_architecture_compiler_generator)


def execute_command(
    cmd: list[str], working_dir_full_path: Path, reporter_sink: ReporterSinkBase
) -> list[str]:  # return errors, if any

    print(cmd)

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
    step: StepCustomCommand, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    # retrieve the current execution context or infer it from the matrix
    res_or_err = select_execution_context(
        context_os_architecture_compiler_generator=step.context_os_architecture_compiler_generator,
        matrix_config=context.get_extra(ContextLocalExecutionActiveMatrixConfig),
    )

    if res_or_err.error is not None:
        report.append_error(res_or_err.error)
        return report

    assert res_or_err.value is not None
    context_os_architecture_compiler_generator = res_or_err.value
    assert context_os_architecture_compiler_generator is not None

    excute_on_matching_context = step.get_extra(StepSkipExecutionOnNonMatchingContext)
    if excute_on_matching_context is not None:
        match = context_os_architecture_compiler_generator.context_os_architecture.is_equal_to(context.os_architecture)
        if not match:
            report.append_info(f"Skip '{step.name}', not compatible with the current context")

    errors = execute_command(step.cmd, context.base_folder_path, reporter_sink)
    for e in errors:
        report.append_error(e)

    return report


def step_custom_command_to_githubwf(
    step: StepCustomCommand, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:

    run_str_list = ["|"]
    run_str_list += step.cmd

    wf_job.steps.append(
        StepRunCommand(
            name=f"Run command {step.name}",
            # if_str=, #TODO add if on OS
            shell_type="bash",
            run=run_str_list,
        )
    )

    return Report()


def validate_step_custom_command(step: StepCustomCommand) -> Report:
    report = Report()
    return report
