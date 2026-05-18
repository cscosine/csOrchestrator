from dataclasses import dataclass, field

from csorchestrator.context.context_local_execution import create_context_local_execution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator, OrchestratorExecutorMinimalDescription
from csorchestrator.orchestrator.orchestrator_executor import OrchestratorExecutorVisitReports, execute_orchestrator
from csorchestrator.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.orchestrator.validated_orchestrator import create_validated_orchestrator
from csorchestrator.visitors.orchestrator_visitor_local_executor import OrchestratorVisitorLocalExecutor


@dataclass
class ExecutionResult:
    # report of the validation phase, which is executed before the execution phase
    report_pre_execution: Report = field(default_factory=Report)
    # description of the execution, which is extracted from the orchestrator
    # before the execution phase
    execution_description: OrchestratorExecutorMinimalDescription = field(default_factory=list)
    # report of the execution phase, which is executed after the validation phase
    report_execution: OrchestratorExecutorVisitReports = field(default_factory=list)


def validate_and_execute_orchestrator(
    orchestrator: Orchestrator, target_folder_path: str, reporter: OrchestratorExecutorReporterBase
) -> ExecutionResult:
    er = ExecutionResult()
    er.execution_description = orchestrator.extract_minimal_description()

    # TODO support reporter also in this phase, at least as report
    contextWithReport = create_context_local_execution(base_folder_path=target_folder_path)
    er.report_pre_execution.append_report(contextWithReport.report)

    if contextWithReport.result is None:
        return er

    context = contextWithReport.result

    # TODO support reporter also in this phase, at least as report
    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)
    er.report_pre_execution.append_report(orchestratorValidatedOpt.report)

    if orchestratorValidatedOpt.result is None:
        return er

    orchestrator = orchestratorValidatedOpt.result

    # execute the orchestrator visitor, which will execute the step to clone the repo
    er.report_execution = execute_orchestrator(
        orchestrator, OrchestratorVisitorLocalExecutor(context=context), reporter=reporter
    )

    return er
