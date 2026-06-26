from collections import Counter
from dataclasses import dataclass, field

from csorchestrator.domain.context.context_os_architecture_compiler_generator import (
    ExecutionMatrixOsArchCompilerGenerator,
)
from csorchestrator.domain.orchestrator.orchestrator import Orchestrator
from csorchestrator.domain.orchestrator.orchestrator_executor import (
    execute_orchestrator,
    executor_visit_reports_has_any_error,
)
from csorchestrator.domain.orchestrator.orchestrator_visitor_base import OrchestratorExecutorVisitReports
from csorchestrator.execution.orchestrator_visitor_validator import OrchestratorVisitorValidator
from csorchestrator.foundation.core.report import Report
from csorchestrator.reporters.orchestrator_executor_reporter_dummy import OrchestratorExecutorReporterDummy


@dataclass
class OrchestratorValidationResultAndReport:
    main_report: Report = field(default_factory=Report)
    validation_reports: OrchestratorExecutorVisitReports = field(default_factory=OrchestratorExecutorVisitReports)
    orchestrator: Orchestrator | None = None

    def has_any_error(self) -> bool:
        return self.main_report.has_errors() or executor_visit_reports_has_any_error(self.validation_reports)


def create_validated_orchestrator(o: Orchestrator) -> OrchestratorValidationResultAndReport:
    validation_report = OrchestratorValidationResultAndReport()

    # check phases name are unique
    phase_names = [p.name for p in o.phases]
    counter_phase_names = Counter(phase_names)
    for name, c in counter_phase_names.items():
        if c > 1:
            validation_report.main_report.append_error(f"phase named {name} has {c} occurrences")

    # check step names are unique in each phase
    for p in o.phases:
        step_names = [s.name for s in p.steps]
        counter_step_names = Counter(step_names)
        for name, c in counter_step_names.items():
            if c > 1:
                validation_report.main_report.append_error(f"in phase {p.name}, step named {name} has {c} occurrences")

    if not isinstance(o.execution_matrix, ExecutionMatrixOsArchCompilerGenerator):
        validation_report.main_report.append_error(
            "execution_matrix needs to be a ExecutionMatrixOsArchCompilerGenerator"
        )
    else:
        # if there are no execution matrix in the list, return error
        if len(o.execution_matrix.os_architecture_compiler_generator_list) == 0:
            validation_report.main_report.append_error("execution matrix list is empty")

    # if so far is validated, use the orchestrator visitor validator to validate the steps, and append the reports
    if len(validation_report.main_report.errors) == 0:
        validation_report.validation_reports = execute_orchestrator(
            o, OrchestratorVisitorValidator(), reporter=OrchestratorExecutorReporterDummy()
        )

    if not validation_report.has_any_error():
        validation_report.orchestrator = o

    return validation_report
