from abc import ABC, abstractmethod
from dataclasses import dataclass

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_minimal_description import OrchestratorExecutorMinimalDescription
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorExecutorVisitReports
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
    def finalize_execution(self) -> None:
        """Called at execution end"""
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

    @abstractmethod
    def report_orchestrator_creation_report(self, report: Report) -> None:
        """Called after the orchestrator creation, with the report of the orchestrator creation"""
        ...

    @abstractmethod
    def report_execution_description(self, execution_description: OrchestratorExecutorMinimalDescription) -> None:
        """Called after extracting the execution description from the orchestrator, with the execution description"""
        ...

    @abstractmethod
    def report_pre_execution_report(self, report: Report) -> None:
        """Called after the pre-execution phase, with the report of the pre-execution phase"""
        ...

    @abstractmethod
    def report_validation_report(self, report: OrchestratorExecutorVisitReports) -> None:
        """Called in the pre-execution phase, with the report of the orchestrator validation"""
        ...

    @abstractmethod
    def report_execution_report(self, report: OrchestratorExecutorVisitReports) -> None:
        """Called after the execution phase, with the report of the execution phase"""
        ...

    @abstractmethod
    def report_start_execution(self, exec_desc: str) -> None:
        """Called before the execution phase, with a description of the execution"""
        ...

    @abstractmethod
    def report_skip_execution(self, exec_desc: str) -> None:
        """Called before the execution phase, with a description of the skipped execution"""
        ...
