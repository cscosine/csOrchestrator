from abc import ABC, abstractmethod
from dataclasses import dataclass

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase


@dataclass
class OrchestratorExecutorReporterBase(ABC):
    @abstractmethod
    def on_init_visit(self) -> None:
        """Called at visit begin"""
        ...

    @abstractmethod
    def on_end_visit(self, visit_complete: bool) -> None:
        """Called at visit end"""
        ...

    @abstractmethod
    def on_begin_phase(self, phase: Phase) -> None:
        """Called before processing a phase"""
        ...

    @abstractmethod
    def on_end_phase(self, phase_complete: bool) -> None:
        """Called after processing completely a phase"""
        ...

    @abstractmethod
    def create_sink_on_begin_visit_step(self, step: StepBase) -> ReporterSinkBase:
        """Called before processing a step"""
        ...

    @abstractmethod
    def on_end_visit_step(self, step: StepBase, report: Report) -> None:
        """Called after processing completely a step"""
        ...
