from dataclasses import dataclass, field
from typing import TypeAlias

from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
    ContextLocalExecutionActiveMatrixConfig,
)
from csorchestrator.context.context_os_architecture import detect_context_os_architecture
from csorchestrator.context.context_os_architecture_compiler_generator import (
    MatrixSkipExecutionOnNonMatchingContext,
    create_context_os_architecture_compiler_generator_string,
)
from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator, OrchestratorExecutorMinimalDescription
from csorchestrator.orchestrator.orchestrator_executor import execute_orchestrator
from csorchestrator.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorExecutorVisitReports
from csorchestrator.orchestrator.validated_orchestrator import create_validated_orchestrator
from csorchestrator.utils.file_system.directory import ensure_directory_exists_or_create_and_is_usable
from csorchestrator.visitors.orchestrator_visitor_local_executor import OrchestratorVisitorLocalExecutor


@dataclass
class ExecutionResult:
    # report of the validation phase, which is executed before the execution phase
    report_pre_execution: Report = field(default_factory=Report)
    # description of the execution, which is extracted from the orchestrator
    # before the execution phase
    execution_description: OrchestratorExecutorMinimalDescription = field(
        default_factory=OrchestratorExecutorMinimalDescription
    )

    # report of each execution phase (can be multiple if matrix is active), which is executed after the validation phase
    # if a matrix cycle is skipped (non executable locally, the list contains a None
    report_executions: list[OrchestratorExecutorVisitReports | None] = field(default_factory=list)


OptionalContextLocalExecutionWithReport: TypeAlias = OptionalResultWithReport[ContextLocalExecution]


def create_context_local_execution(base_folder_path: str) -> OptionalContextLocalExecutionWithReport:
    pr = ensure_directory_exists_or_create_and_is_usable(base_folder_path)

    report = Report()
    report.append_report(pr.report)

    osaExpected = detect_context_os_architecture()

    if osaExpected.error is not None:
        report.append_error(osaExpected.error)

    if pr.result is not None and osaExpected.value is not None:
        return OptionalContextLocalExecutionWithReport.createResultAndReport(
            ContextLocalExecution(base_folder_path=pr.result, os_architecture=osaExpected.value),
            report,
        )
    else:
        return OptionalContextLocalExecutionWithReport.createReport(report)


def validate_and_execute_orchestrator(
    orchestrator: Orchestrator, target_folder_path: str, reporter: OrchestratorExecutorReporterBase
) -> ExecutionResult:
    er = ExecutionResult()
    er.execution_description = orchestrator.extract_minimal_description()
    reporter.report_execution_description(er.execution_description)

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)
    er.report_pre_execution.append_report(orchestratorValidatedOpt.report)

    if orchestratorValidatedOpt.result is None:
        reporter.report_pre_execution_report(er.report_pre_execution)
        reporter.finalize_execution()
        return er

    reporter.report_pre_execution_report(er.report_pre_execution)

    orchestrator = orchestratorValidatedOpt.result

    # validated orchestrator, create context

    contextWithReport = create_context_local_execution(base_folder_path=target_folder_path)
    er.report_pre_execution.append_report(contextWithReport.report)

    if contextWithReport.result is None:
        reporter.report_pre_execution_report(er.report_pre_execution)
        reporter.finalize_execution()
        return er

    context = contextWithReport.result

    matrix = orchestrator.get_execution_matrix()
    if matrix is None:
        reporter.report_start_execution("orchestrator execution without matrix")
        # execute the orchestrator visitor, which will execute the step to clone the repo, build, etc...
        report_execution = execute_orchestrator(
            orchestrator, OrchestratorVisitorLocalExecutor(context=context), reporter=reporter
        )
        reporter.report_execution_report(report_execution)

        er.report_executions.append(report_execution)
    else:
        for os_architecture_compiler_generator in matrix.os_architecture_compiler_generator_list:
            excute_on_matching_context = matrix.get_extra(MatrixSkipExecutionOnNonMatchingContext)
            if excute_on_matching_context is not None:
                match = os_architecture_compiler_generator.context_os_architecture.is_equal_to(context.os_architecture)
                if not match:
                    reporter.report_skip_execution(
                        "skip orchestrator execution on not compatible matrix config: "
                        f"{create_context_os_architecture_compiler_generator_string(os_architecture_compiler_generator)}"
                    )
                    er.report_executions.append(None)
                    continue

            # execute
            reporter.report_start_execution(
                "orchestrator execution on matrix config: "
                f"{create_context_os_architecture_compiler_generator_string(os_architecture_compiler_generator)}"
            )

            context.add_extra(ContextLocalExecutionActiveMatrixConfig(os_architecture_compiler_generator))

            # execute the orchestrator visitor, which will execute the step to clone the repo, build, etc...
            report_execution = execute_orchestrator(
                orchestrator, OrchestratorVisitorLocalExecutor(context=context), reporter=reporter
            )

            context.remove_extra(ContextLocalExecutionActiveMatrixConfig)
            reporter.report_execution_report(report_execution)

            er.report_executions.append(report_execution)

    reporter.finalize_execution()
    return er
