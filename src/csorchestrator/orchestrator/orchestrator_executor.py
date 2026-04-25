from dataclasses import dataclass
from typing import List

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase

OrchestratorExecutorVisitReports = List[List[Report]]  # a list of reports of each step per each phase,


@dataclass
class OrchestratorExecutor:
    orchestrator: Orchestrator

    # return OrchestratorExecutorVisitReports, which is a List[List[Report]], i.e.,
    # - the reports of each step per each phase
    # - in other words, r[phase_index][step_index]
    # the size of the outer and the inner list matches the phases and steps if executions completes without errors
    # in case errors are met, the list is shorter, and the first failing step is the one with the last report
    def execute(self, visitor: OrchestratorVisitorBase) -> OrchestratorExecutorVisitReports:
        visit_complete: bool = True
        visit_reports: OrchestratorExecutorVisitReports = []

        visitor.init_visit()
        for phase in self.orchestrator.phases:
            phase_reports: List[Report] = []
            phase_complete: bool = True

            visitor.begin_phase(phase)
            for step in phase.steps:
                report: Report = visitor.visit_step(step)
                phase_reports.append(report)
                if report.has_errors():
                    phase_complete = False
                    break
            visitor.end_phase(phase_complete)

            visit_reports.append(phase_reports)

            if not phase_complete:
                visit_complete = False
                break

        visitor.end_visit(visit_complete)

        return visit_reports
