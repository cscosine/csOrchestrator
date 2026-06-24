from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.orchestrator.orchestrator_visitor_base import (
    OrchestratorExecutorVisitReports,
    OrchestratorVisitorBase,
)


def executor_visit_reports_has_any_error(oevr: OrchestratorExecutorVisitReports) -> bool:
    rl: list[Report] = [report for phase_reports in oevr for report in phase_reports]
    return any(report.has_errors() for report in rl)


# return OrchestratorExecutorVisitReports, which is a List[List[Report]], i.e.,
# - the reports of each step per each phase
# - in other words, r[phase_index][step_index]
# the size of the outer and the inner list matches the phases and steps if executions completes without errors
# in case errors are met, the list is shorter, and the first failing step is the one with the last report
def execute_orchestrator(
    orchestrator: Orchestrator, visitor: OrchestratorVisitorBase, reporter: OrchestratorExecutorReporterBase
) -> OrchestratorExecutorVisitReports:
    visit_complete: bool = True
    visit_reports: OrchestratorExecutorVisitReports = []

    reporter.on_init_visit()
    visitor.init_visit()
    for phase in orchestrator.phases:
        phase_reports: list[Report] = []
        phase_complete: bool = True

        reporter.on_begin_phase(phase)
        visitor.begin_phase(phase)
        for step in phase.steps:
            reporter_sink = reporter.create_sink_on_begin_visit_step(step)
            report: Report = visitor.visit_step(step, reporter_sink=reporter_sink)

            reporter.on_end_visit_step(step, report)

            phase_reports.append(report)
            if report.has_errors():
                phase_complete = False
                break

        reporter.on_end_phase(phase_complete)
        visitor.end_phase(phase_complete)

        visit_reports.append(phase_reports)

        if not phase_complete:
            visit_complete = False
            break

    reporter.on_end_visit(visit_complete)
    visitor.end_visit(visit_complete)

    return visit_reports
