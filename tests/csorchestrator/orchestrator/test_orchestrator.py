from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.step.step_echo_message import StepEchoMessage


def test_orchestrator_add_phases() -> None:
    o = Orchestrator()

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
