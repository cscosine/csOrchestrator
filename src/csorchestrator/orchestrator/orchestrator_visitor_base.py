from abc import ABC, abstractmethod
from dataclasses import dataclass

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase

# external list per phase, internal per steps
OrchestratorExecutorVisitReports = list[list[Report]]  # a list of reports of each step per each phase,


@dataclass
class OrchestratorVisitorBase(ABC):
    @abstractmethod
    def init_visit(self) -> None:
        """Called at visit begin"""
        ...

    @abstractmethod
    def end_visit(self, visit_complete: bool) -> None:
        """Called at visit end"""
        ...

    @abstractmethod
    def begin_phase(self, phase: Phase) -> None:
        """Called before processing a phase"""
        ...

    @abstractmethod
    def end_phase(self, phase_complete: bool) -> None:
        """Called after processing completely a phase"""
        ...

    @abstractmethod
    def visit_step(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        """Called to visit a step"""
        ...
