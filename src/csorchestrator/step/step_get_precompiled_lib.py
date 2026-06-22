from dataclasses import dataclass

from csorchestrator.ci.github.github_workflow_config import JobOrchestratorMatrixExecution
from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase, StepValidatorBase, StepValidatorNoOp


@dataclass
class StepGetPrecompiledLib(StepBase):
    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report()  # TODO impl

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report()  # TODO impl

    @classmethod
    def createValidator(cls) -> StepValidatorBase:
        return StepValidatorNoOp()
