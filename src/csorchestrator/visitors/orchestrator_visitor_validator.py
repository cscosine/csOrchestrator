from dataclasses import dataclass, field

from csorchestrator.domain.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.domain.orchestrator.phase import Phase
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import StepBase, StepValidatorBase
from csorchestrator.foundation.core.report import Report


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
