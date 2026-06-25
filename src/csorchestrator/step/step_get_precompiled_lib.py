from dataclasses import dataclass

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import (
    JobOrchestratorMatrixExecution,
    StepBase,
    StepValidatorBase,
    StepValidatorNoOp,
)
from csorchestrator.foundation.core.report import Report


@dataclass
class StepGetPrecompiledLib(StepBase):
    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report()  # TODO impl

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report()  # TODO impl

    @classmethod
    def createValidator(cls) -> StepValidatorBase:
        return StepValidatorNoOp()
