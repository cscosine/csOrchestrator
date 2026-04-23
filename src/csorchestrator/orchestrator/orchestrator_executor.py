from dataclasses import dataclass

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.validated_orchestrator import ValidatedOrchestrator


@dataclass
class OrchestratorExecutor:
    validated_orchestrator: ValidatedOrchestrator

    def execute(self, visitor: OrchestratorVisitorBase) -> None:
        visit_complete: bool = True

        visitor.init_visit()
        for phase in self.validated_orchestrator.orchestrator.phases:
            phase_complete: bool = True

            visitor.begin_phase(phase)
            for step in phase.steps:
                report: Report = visitor.visit_step(step)
                if report.has_errors():
                    phase_complete = False
                    break
            visitor.end_phase(phase_complete)

            if not phase_complete:
                visit_complete = False
                break

        visitor.end_visit(visit_complete)
