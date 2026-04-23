from dataclasses import dataclass

from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.validated_orchestrator import ValidatedOrchestrator


@dataclass
class OrchestratorExecutor:
    validated_orchestrator: ValidatedOrchestrator

    def execute(self, visitor: OrchestratorVisitorBase) -> None:
        visitor.init_visit()
        for phase in self.validated_orchestrator.orchestrator.phases:
            visitor.begin_phase(phase)
            for step in phase.steps:
                visitor.visit_step(step)
            visitor.end_phase()
        visitor.end_visit()
