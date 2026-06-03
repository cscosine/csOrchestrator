from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from csorchestrator.ci.github.github_workflow_config import (
    JobOrchestratorMatrixExecution,
    MatrixOsArchCompilerGeneratorRunnerEntryInclude,
    StepRunCommand,
)
from csorchestrator.context.context_compiler_generator import GeneratorType
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
    ContextLocalExecutionActiveMatrixConfig,
)
from csorchestrator.context.context_os_architecture_compiler_generator import ContextOsArchitectureCompilerGenerator
from csorchestrator.core.expected import Expected
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase, StepSkipExecutionOnNonMatchingContext
from csorchestrator.step.step_custom_command import execute_command
from csorchestrator.utils.presets.supported_variants import (
    BuildConfig,
    ContextOsArchitectureCompilerGeneratorConfig,
    get_all_supported_workflow_descriptions,
    get_supported_build_configs_for_generator_type,
    is_config_selected_for_generator,
    workflow_name_from_components,
    workflow_name_from_description,
)


@dataclass
class StepCMakeWorkflow(StepBase):
    source_dir: str

    config: BuildConfig

    context_os_architecture_compiler_generator: ContextOsArchitectureCompilerGenerator | None = None

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
            context_os_architecture_compiler_generator=ContextOsArchitectureCompilerGenerator(
                workflow_description.context_os_architecture, workflow_description.context_compiler_generator
            ),
            config=workflow_description.config,
        )


ContextWorkflowsExpected: TypeAlias = Expected[
    tuple[
        ContextOsArchitectureCompilerGenerator,
        list[ContextOsArchitectureCompilerGeneratorConfig],
    ],
    str,
]


def get_context_and_workflows(
    config: BuildConfig,
    context_os_architecture_compiler_generator: ContextOsArchitectureCompilerGenerator | None,
    matrix_config: ContextLocalExecutionActiveMatrixConfig | None,
) -> ContextWorkflowsExpected:

    if context_os_architecture_compiler_generator is None:
        # no context, inherit it from the matrix config if any

        if matrix_config is None:
            return ContextWorkflowsExpected.make_error("no matrix config specified")

        context_os_architecture_compiler_generator = matrix_config.active_os_architecture_compiler_generator

        workflow_configs = get_all_supported_workflow_descriptions(
            selected_config=config,
            os_arch_generator=context_os_architecture_compiler_generator,
        )

        if len(workflow_configs) == 0:
            return ContextWorkflowsExpected.make_error("no workflows are supported in the current execution context")

    else:
        # has context, use it as a single workflow config step

        workflow_configs = [
            ContextOsArchitectureCompilerGeneratorConfig(
                context_os_architecture_compiler_generator.context_os_architecture,
                context_os_architecture_compiler_generator.context_compiler_generator,
                config,
            )
        ]

    assert context_os_architecture_compiler_generator is not None
    return ContextWorkflowsExpected.make_value((context_os_architecture_compiler_generator, workflow_configs))


def execute_step_cmake_workflow(
    step: StepCMakeWorkflow, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    # retrieve the current execution context or infer it from the matrix
    res_or_err = get_context_and_workflows(
        config=step.config,
        context_os_architecture_compiler_generator=step.context_os_architecture_compiler_generator,
        matrix_config=context.get_extra(ContextLocalExecutionActiveMatrixConfig),
    )

    if res_or_err.error is not None:
        report.append_error(res_or_err.error)
        return report

    assert res_or_err.value is not None
    context_os_architecture_compiler_generator, workflow_configs = res_or_err.value
    assert context_os_architecture_compiler_generator is not None

    for workflow_config in workflow_configs:
        workflow_name = workflow_name_from_description(workflow_config)

        excute_on_matching_context = step.get_extra(StepSkipExecutionOnNonMatchingContext)
        if excute_on_matching_context is not None:
            match = context_os_architecture_compiler_generator.context_os_architecture.is_equal_to(
                context.os_architecture
            )
            if not match:
                report.append_info(f"Skip '{workflow_name}', not compatible with the current context")
                continue

        target_full_path: Path = context.base_folder_path / step.source_dir
        cmd = [
            "cmake",
            "--workflow",
            "--preset",
            workflow_name,
        ]
        errors = execute_command(cmd, target_full_path, reporter_sink)
        for e in errors:
            report.append_error(e)

        if report.has_errors():
            return report  # early exit

    return report


def step_cmake_workflow_to_githubwf(
    step: StepCMakeWorkflow, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:

    # create two mutually exclusive steps, one for single config generators and one for multi config
    for generator_type in [GeneratorType.SINGLE_CONFIG, GeneratorType.MULTI_CONFIG]:
        generator_supported_configs = get_supported_build_configs_for_generator_type(generator_type)
        selected_configs = []
        for supported_config in generator_supported_configs:
            if is_config_selected_for_generator(
                generator_type, current_config=supported_config, requested_config=step.config
            ):
                selected_configs += [supported_config]

        if len(selected_configs) == 0:
            return Report().append_error(
                f"Requested config {step.config.value} is not supported for generator type {generator_type.value}"
            )

        run_str_list = ["|", "set -e"]
        for config in selected_configs:
            wf_name = workflow_name_from_components(
                MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_NAME_EMBRACED,
                MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_OS_VERSION_EMBRACED,
                MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_ARCHITECTURE_EMBRACED,
                MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_ARCHITECTURE_VARIANT_EMBRACED,
                MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_COMPILER_EMBRACED,
                MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_COMPILER_VERSION_EMBRACED,
                MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_GENERATOR_EMBRACED,
                config.value,
            )
            run_str_list += ["cmake --workflow " + wf_name]

        generator_type_matrix = MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_GENERATOR_TYPE

        wf_job.steps.append(
            StepRunCommand(
                name=f"cmake workflow on {step.name} - ({generator_type.value})",
                if_str=f"{generator_type_matrix} == '{generator_type.value}'",
                shell_type="bash",
                run=run_str_list,
                working_directory=step.source_dir,
            )
        )

    return Report()


def validate_step_cmake_workflow(step: StepCMakeWorkflow) -> Report:
    report = Report()
    return report
