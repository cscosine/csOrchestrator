from dataclasses import dataclass
from typing import List

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.validated_orchestrator import ValidatedOrchestrator

OrchestratorExecutorVisitReports = List[List[Report]]


@dataclass
class OrchestratorExecutor:
    validated_orchestrator: ValidatedOrchestrator

    def execute(self, visitor: OrchestratorVisitorBase) -> OrchestratorExecutorVisitReports:
        visit_complete: bool = True
        visit_reports: OrchestratorExecutorVisitReports = []

        visitor.init_visit()
        for phase in self.validated_orchestrator.orchestrator.phases:
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
