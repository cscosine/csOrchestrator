from collections import Counter
from typing import Optional, TypeAlias

from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.orchestrator_executor import (
    execute_orchestrator,
    flatten_orchestrator_executor_visit_reports,
)
from csorchestrator.reporters.orchestrator_executor_reporter_dummy import OrchestratorExecutorReporterDummy
from csorchestrator.visitors.orchestrator_visitor_validator import OrchestratorVisitorValidator

OptionalValidatedOrchestratorWithReport: TypeAlias = OptionalResultWithReport[Orchestrator]


# return none if ok, the string error otherwise
def validPhaseStepName(name: str) -> Optional[str]:
    if name.count(".") > 0:
        return "name cannot contains '.'"
    return None


def create_validated_orchestrator(o: Orchestrator) -> OptionalValidatedOrchestratorWithReport:
    report = Report()

    # check phases name are unique
    phase_names = [p.name for p in o.phases]
    for name in phase_names:
        err_msg = validPhaseStepName(name) is not None
        if err_msg:
            report.append_error(f"phase name {name} is invalid, {err_msg}")

    counter_phase_names = Counter(phase_names)
    for name, c in counter_phase_names.items():
        if c > 1:
            report.append_error(f"phase named {name} has {c} occurrences")

    # check step names are unique in each phase
    for p in o.phases:
        step_names = [s.name for s in p.steps]
        for name in step_names:
            err_msg = validPhaseStepName(name) is not None
            if err_msg:
                report.append_error(f"step name {name} is invalid, {err_msg}")

        counter_step_names = Counter(step_names)
        for name, c in counter_step_names.items():
            if c > 1:
                report.append_error(f"in phase {p.name}, step named {name} has {c} occurrences")

    # if so far is validated, use the orchestrator visitor validator to validate the steps, and append the reports
    if len(report.errors) == 0:
        visit_report = execute_orchestrator(
            o, OrchestratorVisitorValidator(), reporter=OrchestratorExecutorReporterDummy()
        )
        report.append_report(flatten_orchestrator_executor_visit_reports(visit_report))

    if len(report.errors) > 0:
        return OptionalValidatedOrchestratorWithReport.createReport(report)
    return OptionalValidatedOrchestratorWithReport.createResultAndReport(o, report)
