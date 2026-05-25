import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TextIO

from csorchestrator.context.context_compiler_generator import ContextCompilerGenerator
from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.context.context_os_architecture import ContextOsArchitecture
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase, StepExecuteOnMatchingContext
from csorchestrator.utils.presets.supported_variants import (
    BuildConfig,
    ContextOsArchitectureCompilerGeneratorConfig,
    workflow_name_from_description,
)


@dataclass
class StepCMakeWorkflow(StepBase):
    source_dir: str

    config: BuildConfig

    context_os_architecture: ContextOsArchitecture | None = None
    context_compiler_generator: ContextCompilerGenerator | None = None

    @classmethod
    def create_from_workflow_description(
        cls,
        name: str,
        description: str,
        source_dir: str,
        workflow_description: ContextOsArchitectureCompilerGeneratorConfig,
    ) -> "StepCMakeWorkflow":
        return cls(
            name=name,
            description=description,
            source_dir=source_dir,
            context_os_architecture=workflow_description.context_os_architecture,
            context_compiler_generator=workflow_description.context_compiler_generator,
            config=workflow_description.config,
        )


def execute_step_cmake_workflow(
    step: StepCMakeWorkflow, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    context_os_architecture = step.context_os_architecture
    if context_os_architecture is None:
        context_os_architecture = context.os_architecture
    if context_os_architecture is None:
        report.append_error(
            f"context_os_architecture is None for {step.name}, please provide it in the execution matrix or in the step"
        )
        return report

    context_compiler_generator = step.context_compiler_generator
    if context_compiler_generator is None:
        context_compiler_generator = None  # TODO how to retrieve from context?!?
    if context_compiler_generator is None:
        report.append_error(
            f"context_compiler_generator is None for {step.name},"
            "please provide it in the execution matrix or in the step"
        )
        return report

    workflow_name = workflow_name_from_description(
        ContextOsArchitectureCompilerGeneratorConfig(context_os_architecture, context_compiler_generator, step.config)
    )

    excute_on_matching_context = step.get_extra(StepExecuteOnMatchingContext)
    if excute_on_matching_context is not None:
        match = context_os_architecture.is_equal_to(context.os_architecture)
        if not match:
            report.append_info(f"Skip '{workflow_name}', not compatible with the current context")
            return report

    target_full_path: Path = context.base_folder_path / step.source_dir
    cmd = [
        "cmake",
        "--workflow",
        "--preset",
        workflow_name,
    ]

    process = subprocess.Popen(
        cmd,
        cwd=str(target_full_path),
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
        report.append_error(f"Failed to run cmake workflow: {e}")
        return report

    stdout_thread.join()
    stderr_thread.join()

    if return_code != 0:
        report.append_error(f"CMake workflow '{workflow_name}' failed with exit code {return_code}")
    # success => empty report
    return report


def validate_step_cmake_workflow(step: StepCMakeWorkflow) -> Report:
    report = Report()
    return report
