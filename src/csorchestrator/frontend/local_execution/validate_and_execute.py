from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from csorchestrator.domain.context.context_os_architecture import ContextOsArchitecture, detect_context_os_architecture
from csorchestrator.domain.context.context_os_architecture_compiler_generator import (
    ExecutionMatrixOsArchCompilerGenerator,
    create_context_os_architecture_compiler_generator_string,
)
from csorchestrator.domain.execution.execution import ExecutionResult
from csorchestrator.domain.orchestrator.orchestrator import Orchestrator
from csorchestrator.domain.orchestrator.orchestrator_executor import (
    execute_orchestrator,
    executor_visit_reports_has_any_error,
)
from csorchestrator.domain.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.foundation.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.foundation.core.report import Report
from csorchestrator.foundation.file_system.directory import ensure_directory_exists_or_create_and_is_usable
from csorchestrator.frontend import release_manifest
from csorchestrator.frontend.local_execution.context_local_execution import (
    ContextLocalExecution,
    ContextLocalExecutionExtra,
)
from csorchestrator.frontend.local_execution.orchestrator_visitor_local_executor import OrchestratorVisitorLocalExecutor
from csorchestrator.frontend.release_manifest.manifest import (
    ManifestVersionsEntry,
    create_release_manifest,
    write_release_manifest,
)
from csorchestrator.frontend.step.step_get_versions_from_cmake_config_package_version import (
    create_version_file_name,
    load_version_file,
)
from csorchestrator.frontend.step.step_upload_artifacts import create_artifact_prefix_from_orchestrator_name_version
from csorchestrator.frontend.validation.validated_orchestrator import create_validated_orchestrator


@dataclass
class OsArchitectureAndPath:
    os_architecture: ContextOsArchitecture
    path: Path


OptionalOsArchitectureAndPathWithReport: TypeAlias = OptionalResultWithReport[OsArchitectureAndPath]


def _create_context_os_architecture_string(
    os_architecture: ContextOsArchitecture,
) -> str:
    parts: list[str] = []
    parts.append(os_architecture.os.value.lower())
    parts.append(os_architecture.os_version.lower())
    parts.append(os_architecture.architecture.value.lower())
    parts.append(os_architecture.architecture_variant.lower())
    return "-".join(parts)


def create_os_and_path(base_folder_path: str) -> OptionalOsArchitectureAndPathWithReport:
    report = Report()

    pr = ensure_directory_exists_or_create_and_is_usable(base_folder_path)

    if pr.error is not None:
        report.append_error(pr.error)

    osaExpected = detect_context_os_architecture()

    if osaExpected.error is not None:
        report.append_error(osaExpected.error)

    if pr.value is not None and osaExpected.value is not None:
        return OptionalOsArchitectureAndPathWithReport.createResultAndReport(
            OsArchitectureAndPath(os_architecture=osaExpected.value, path=pr.value),
            report,
        )
    else:
        return OptionalOsArchitectureAndPathWithReport.createReport(report)


def validate_and_execute_orchestrator(
    orchestrator: Orchestrator, target_folder_path: str, reporter: OrchestratorExecutorReporterBase
) -> ExecutionResult:
    er = ExecutionResult()
    er.execution_description = orchestrator.extract_minimal_description()
    reporter.report_execution_description(er.execution_description)

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)
    er.report_pre_execution.append_report(orchestratorValidatedOpt.main_report)
    er.report_validation = orchestratorValidatedOpt.validation_reports
    reporter.report_validation_report(er.report_validation)

    if orchestratorValidatedOpt.orchestrator is None:
        reporter.report_pre_execution_report(er.report_pre_execution)
        reporter.finalize_execution()
        return er

    orchestrator = orchestratorValidatedOpt.orchestrator

    # validated orchestrator, create context

    os_and_path_opt = create_os_and_path(base_folder_path=target_folder_path)
    er.report_pre_execution.append_report(os_and_path_opt.report)

    if os_and_path_opt.result is None:
        reporter.report_pre_execution_report(er.report_pre_execution)
        reporter.finalize_execution()
        return er

    # finalized the pre execution
    reporter.report_pre_execution_report(er.report_pre_execution)

    os_and_path = os_and_path_opt.result

    matrix = orchestrator.execution_matrix

    matrix_extras: dict[type, ContextLocalExecutionExtra] = {}
    counter: int = 0

    assert isinstance(matrix, ExecutionMatrixOsArchCompilerGenerator)  # ensured by the validator

    # matrix execution

    for os_architecture_compiler_generator in matrix.os_architecture_compiler_generator_list:
        match = os_architecture_compiler_generator.context_os_architecture.can_be_executed_on(
            os_and_path.os_architecture
        )
        if not match:
            reporter.report_skip_execution(
                "skip orchestrator execution on not compatible matrix config: "
                f"{create_context_os_architecture_compiler_generator_string(os_architecture_compiler_generator)}"
                f", current os and architecture:  {_create_context_os_architecture_string(os_and_path.os_architecture)}"
            )
            er.report_executions.append(None)
            continue
        # use the compatible os_arcchitecture, not the detected one.
        # e.g. detected os is win 11, but we select win 10 in the matrix, which is compatible

        context = ContextLocalExecution(
            base_folder_path=os_and_path.path,
            os_architecture=os_architecture_compiler_generator.context_os_architecture,
            active_compiler_generator=os_architecture_compiler_generator.context_compiler_generator,
            matrix_extras=matrix_extras,
            matrix_execution_id=str(counter),
        )

        # execute
        reporter.report_start_execution(
            "orchestrator execution on matrix config: "
            f"{create_context_os_architecture_compiler_generator_string(os_architecture_compiler_generator)}"
        )

        # execute the orchestrator visitor, which will execute the step to clone the repo, build, etc...
        report_execution = execute_orchestrator(
            orchestrator, OrchestratorVisitorLocalExecutor(context=context), reporter=reporter
        )

        if executor_visit_reports_has_any_error(report_execution):
            reporter.report_execution_report(report_execution)
            er.report_executions.append(report_execution)
            break

        reporter.report_execution_report(report_execution)

        er.report_executions.append(report_execution)

        # keep the matrix_extras modified for the next context
        matrix_extras = context.matrix_extras
        counter += 1

    reporter.finalize_execution()

    # end matrix execution, execute the release part if any
    if (
        orchestrator.wf_config is not None
        and orchestrator.wf_config.create_release_on_tag is not None
        and orchestrator.wf_config.create_release_on_tag.publish_cs_orchestrator_manifest
    ):
        # first: matrix element string, second packages,version list
        collected_version_entries: list[ManifestVersionsEntry] = []
        base_install_dir = orchestrator.wf_config.create_release_on_tag.base_install_dir

        for os_architecture_compiler_generator in matrix.os_architecture_compiler_generator_list:
            match = os_architecture_compiler_generator.context_os_architecture.can_be_executed_on(
                os_and_path.os_architecture
            )
            if not match:
                # TODO introduce a new report section and report skipped
                continue
            # use the compatible os_arcchitecture, not the detected one.
            # e.g. detected os is win 11, but we select win 10 in the matrix, which is compatible

            context = ContextLocalExecution(
                base_folder_path=os_and_path.path,
                os_architecture=os_architecture_compiler_generator.context_os_architecture,
                active_compiler_generator=os_architecture_compiler_generator.context_compiler_generator,
                matrix_extras=matrix_extras,
                matrix_execution_id=str(counter),
            )

            context_os_architecture_compiler_generator_string = (
                create_context_os_architecture_compiler_generator_string(
                    context.get_active_os_architecture_compiler_generator()
                )
            )

            input_base_dir = Path(context.base_folder_path / base_install_dir).resolve()
            input_full_path = Path(
                input_base_dir / Path(create_version_file_name(context_os_architecture_compiler_generator_string))
            ).resolve()

            packages = load_version_file(input_full_path)
            collected_version_entries.append(
                ManifestVersionsEntry(context_os_architecture_compiler_generator_string, packages)
            )
        release_manifest = create_release_manifest(collected_version_entries)
        write_release_manifest(
            release_manifest,
            base_install_dir
            / Path(create_artifact_prefix_from_orchestrator_name_version(orchestrator) + "csorchestrator.manifest"),
        )

    return er
