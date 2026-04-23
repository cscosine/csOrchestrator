from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import singledispatchmethod

from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.step_base import StepBase


@dataclass
class OrchestratorVisitorBase(ABC):
    VISIT_WITH_STEP_BASE_NOT_IMPL_ERROR: str = (
        "OrchestratorVisitorBase::visit_step(self, step : StepBase) should never be reached, "
        "concrete visitors should implement visit via their own singledispatchmethod"
    )

    @abstractmethod
    def init_visit(self) -> None:
        """Called at visit begin"""
        ...

    @abstractmethod
    def end_visit(self) -> None:
        """Called at visit end"""
        ...

    @abstractmethod
    def begin_phase(self, phase: Phase) -> None:
        """Called before processing a phase"""
        ...

    @abstractmethod
    def end_phase(self) -> None:
        """Called after processing completely a phase"""
        ...

    def visit_step(self, step: StepBase) -> None:
        self.visit_step_base(step)

    @abstractmethod
    def visit_step_base(self, step: StepBase) -> None:
        """Called when ``visit_step`` encounters a step type with no registered
        handler.  Concrete visitors **must** implement this to decide the
        policy for unregistered step types (raise, skip, log, etc.)."""
        ...

    @staticmethod
    def create_visit_dispatch() -> singledispatchmethod:  # type: ignore[type-arg]
        """Return a fresh singledispatchmethod that concrete visitors should
        assign as their own ``visit_step``.  Use ``@visit.register`` inside the
        class body to register handlers for specific step types.

        Unhandled step types fall through to ``visit_step_base``, which
        every concrete visitor must implement.

        Example::

            class MyVisitor(OrchestratorVisitorBase):
                visit_step = OrchestratorVisitorBase.create_visit_dispatch()

                @visit_step.register
                def _(self, step: SomeStep):
                    ...

                def visit_step_base(self, step: StepBase) -> None:
                    raise NotImplementedError(f"Unhandled {type(step)}")
        """

        @singledispatchmethod
        def visit_step(self: "OrchestratorVisitorBase", step: StepBase) -> None:
            self.visit_step_base(step)

        return visit_step
