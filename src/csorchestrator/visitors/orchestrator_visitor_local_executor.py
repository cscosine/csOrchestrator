from dataclasses import dataclass

from csorchestrator.domain.context.context_local_execution import ContextLocalExecution
from csorchestrator.domain.context.step_utils import (
    StepExecuteOnlyOn,
    StepExecuteOnlyOncePerMatrix,
    StepSkipExecutionOnLocal,
)
from csorchestrator.domain.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.domain.orchestrator.phase import Phase
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import StepBase, StepCapability
from csorchestrator.foundation.core.report import Report


@dataclass
class StepCapabilityLocalExecution(StepCapability):
    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report().append_error("StepCapabilityLocalExecution.execute_locally need to be imlemented in subclasses")


@dataclass
class OrchestratorVisitorLocalExecutor(OrchestratorVisitorBase):
    context: ContextLocalExecution
    _current_phase_name: str | None = None

    def init_visit(self) -> None:
        pass

    def end_visit(self, visit_complete: bool) -> None:
        pass

    def begin_phase(self, phase: Phase) -> None:
        self._current_phase_name = phase.name

    def end_phase(self, phase_complete: bool) -> None:
        self._current_phase_name = None

    def visit_step(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        skip_reason = self._should_execute_step(step)
        if skip_reason is not None:
            return Report().append_info(f"skipping execution of step {step.name} since {skip_reason}")

        capability = step.get_capability(StepCapabilityLocalExecution)
        if capability is None:
            return Report().append_info(f"skip step {step.name} because it does not support local execution")
        return capability.execute_locally(self.context, reporter_sink)

    def _should_execute_step(self, step: StepBase) -> None | str:  # None is non expected error
        if self._current_phase_name is None:
            return "Failed to determine current phase - unexpected error in _should_execute_step"

        # manage skip on local execution
        if step.get_extra(StepSkipExecutionOnLocal) is not None:
            return "Step is marked to be skipped on local execution"

        # manage skip on non matching OS
        execute_only_on_extra = step.get_extra(StepExecuteOnlyOn)
        if execute_only_on_extra is not None:
            result = execute_only_on_extra.evaluate_local_exec(self.context)
            if result is not None:
                return result

        # manage single execution per matrix
        exec_only_one = step.get_extra(StepExecuteOnlyOncePerMatrix)
        if exec_only_one is not None:
            result = exec_only_one.evaluate_local_exec(self.context, self._current_phase_name, step.name)
            if result is not None:
                return result
        return None
