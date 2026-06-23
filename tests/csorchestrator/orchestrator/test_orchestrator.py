from dataclasses import dataclass

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.core.report import Report
from csorchestrator.execution.factory import create_orchestrator_factory
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import (
    JobOrchestratorMatrixExecution,
    StepBase,
    StepValidatorBase,
    StepValidatorNoOp,
)


@dataclass
class StepEchoMessage(StepBase):
    message: str

    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report()

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return Report()

    @classmethod
    def createValidator(cls) -> StepValidatorBase:
        return StepValidatorNoOp()


def test_orchestrator_add_phases() -> None:
    o = create_orchestrator_factory("myName", "0.0.0", "exec-job")

    p = Phase("phase_1").add_step(StepEchoMessage(name="p1s1", description="p1 step s1", message="phase 1 step 2"))
    p.add_step(StepEchoMessage(name="p1s2", description="p1 step s2", message="phase 1 step 2"))
    pb = Phase("phase_1b").add_step(StepEchoMessage(name="p1bs1", description="p1b step s1", message="phase 1b step 2"))

    o.add_phase(p).add_phase(pb)

    o.create_phase("phase_2").add_step(
        StepEchoMessage(name="p2s1", description="p2 step s1", message="phase 2 step 1")
    ).add_step(StepEchoMessage(name="p2s2", description="p2 step s2", message="phase 2 step 2")).add_step(
        StepEchoMessage(name="p2s2", description="p2 step s2", message="phase 2 step 3")
    )

    assert len(o.phases) == 3
    assert len(o.phases[0].steps) == 2
    assert len(o.phases[1].steps) == 1
    assert len(o.phases[2].steps) == 3


# ------------------------------------------------------------------------------------------------


def test_orchestrator_executor_minimal_description() -> None:
    o = create_orchestrator_factory("myName", "0.0.0", "exec-job")

    o.create_phase("p1").add_step(StepEchoMessage(name="p1s1", description="p1 step s1", message="")).add_step(
        StepEchoMessage(name="p1s2", description="p1 step s2", message="")
    ).add_step(StepEchoMessage(name="p1s3", description="p1 step s3", message=""))

    o.create_phase("p2").add_step(StepEchoMessage(name="p2s1", description="p2 step s1", message="")).add_step(
        StepEchoMessage(name="p2s2", description="p2 step s2", message="")
    )

    min_desc = o.extract_minimal_description()
    od = min_desc.phases_and_steps

    assert len(od) == 2

    # phases
    assert od[0].phase_name == "p1"
    assert od[1].phase_name == "p2"

    # steps
    assert len(od[0].step_names) == 3
    assert od[0].step_names[0] == "p1s1"
    assert od[0].step_names[1] == "p1s2"
    assert od[0].step_names[2] == "p1s3"

    assert len(od[1].step_names) == 2
    assert od[1].step_names[0] == "p2s1"
    assert od[1].step_names[1] == "p2s2"
