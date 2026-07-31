from dataclasses import dataclass, field

from csorchestrator.domain.orchestrator.orchestrator_executor import (
    executor_visit_reports_has_any_error,
)
from csorchestrator.domain.orchestrator.orchestrator_minimal_description import OrchestratorExecutorMinimalDescription
from csorchestrator.domain.orchestrator.orchestrator_visitor_base import OrchestratorExecutorVisitReports
from csorchestrator.foundation.core.report import Report


@dataclass
class ExecutionResult:
    # report of the validation phase, which is executed before the execution phase
    report_validation: OrchestratorExecutorVisitReports = field(default_factory=OrchestratorExecutorVisitReports)
    # report of the pre execution, before validation
    report_pre_execution: Report = field(default_factory=Report)
    # description of the execution, which is extracted from the orchestrator
    # before the execution phase
    execution_description: OrchestratorExecutorMinimalDescription | None = None

    # report of each execution phase (can be multiple if matrix is active), which is executed after the validation phase
    # if a matrix cycle is skipped (non executable locally, the list contains a None
    # if the matrix execution terminates before completing all the cycles (e.g. error in one of the cycle),
    #   the list contains only the executed cycles report, and then it is terminated
    #   (e.g. if 3 cycles, and error in the second, the list contains [report_cycle_1, report_cycle_2],
    #   and then it is terminated, without the report of the cycle 3)
    report_executions: list[OrchestratorExecutorVisitReports | None] = field(default_factory=list)

    # report the post execution steps results
    report_post_execution: list[Report] = field(default_factory=list)

    def is_execution_successful(
        self,
    ) -> bool:
        if self.report_pre_execution.has_errors():
            return False

        for exec in self.report_executions:
            if exec is not None and executor_visit_reports_has_any_error(exec):
                return False
        return True
