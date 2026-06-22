from dataclasses import dataclass, field

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase, StepValidatorBase


@dataclass
class OrchestratorVisitorValidator(OrchestratorVisitorBase):
    _step_validators_per_type: dict[type[StepBase], StepValidatorBase] = field(default_factory=dict)

    def init_visit(self) -> None:
        self._step_validators_per_type.clear()

    def end_visit(self, visit_complete: bool) -> None:
        pass

    def begin_phase(self, phase: Phase) -> None:
        pass

    def end_phase(self, phase_complete: bool) -> None:
        pass

    def visit_step(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        step_type = type(step)

        validator = self._step_validators_per_type.get(step_type)

        if validator is None:
            validator = step_type.createValidator()
            self._step_validators_per_type[step_type] = validator

        return validator.validate(step)
