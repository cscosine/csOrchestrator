from dataclasses import dataclass, field

from csorchestrator.context.context_local_execution import create_context_local_execution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator, OrchestratorExecutorMinimalDescription
from csorchestrator.orchestrator.orchestrator_executor import OrchestratorExecutor, OrchestratorExecutorVisitReports
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


def validate_and_execute_orchestrator(orchestrator: Orchestrator, target_folder_path: str) -> ExecutionResult:
    er = ExecutionResult()
    er.execution_description = orchestrator.extract_minimal_description()

    contextWithReport = create_context_local_execution(path=target_folder_path)
    er.report_pre_execution.append_report(contextWithReport.report)

    if contextWithReport.result is None:
        return er

    context = contextWithReport.result

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)
    er.report_pre_execution.append_report(orchestratorValidatedOpt.report)

    if orchestratorValidatedOpt.result is None:
        return er

    orchestrator = orchestratorValidatedOpt.result

    orchestrator_visitor = OrchestratorVisitorLocalExecutor(context=context)

    executor = OrchestratorExecutor(orchestrator)

    # execute the orchestrator visitor, which will execute the step to clone the repo
    er.report_execution = executor.execute(orchestrator_visitor)

    return er
