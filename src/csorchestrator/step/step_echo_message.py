from dataclasses import dataclass

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase


@dataclass
class StepEchoMessage(StepBase):
    message: str


def execute_step_echo_message(
    step: StepEchoMessage, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:

    _ = context

    reporter_sink.stdout(f"{step.message}")

    return Report()
