from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.validated_orchestrator import (
    create_validated_orchestrator,
)
from csorchestrator.step.step_echo_message import StepEchoMessage


def test_orchestrator_add_phases() -> None:
    # valid, no repetition in phases or step
    o = Orchestrator()
    o.add_phase(Phase("p1").add_step(StepEchoMessage("s1", "", "")).add_step(StepEchoMessage("s2", "", ""))).add_phase(
        Phase("p2").add_step(StepEchoMessage("s1", "", "")).add_step(StepEchoMessage("s2", "", ""))
    )
    vr = create_validated_orchestrator(o)
    assert vr.has_result()
    assert vr.result == o
    assert len(vr.report.errors) == 0
    assert len(vr.report.warnings) == 0
    assert len(vr.report.infos) == 0

    # invalid, repetition in phases names
    o = Orchestrator()
    o.add_phase(Phase("p").add_step(StepEchoMessage("s1", "", ""))).add_phase(
        Phase("p").add_step(StepEchoMessage("s1", "", ""))
    )
    vr = create_validated_orchestrator(o)
    assert not vr.has_result()
    assert len(vr.report.errors) == 1
    assert len(vr.report.warnings) == 0
    assert len(vr.report.infos) == 0

    # invalid, repetition in step names
    o = Orchestrator()
    o.add_phase(Phase("p").add_step(StepEchoMessage("s", "", "")).add_step(StepEchoMessage("s", "", "")))
    vr = create_validated_orchestrator(o)
    assert not vr.has_result()
    assert len(vr.report.errors) == 1
    assert len(vr.report.warnings) == 0
    assert len(vr.report.infos) == 0

    # invalid, repetition in both phases and step names
    o = Orchestrator()
    o.add_phase(Phase("p").add_step(StepEchoMessage("s", "", "")).add_step(StepEchoMessage("s", "", ""))).add_phase(
        Phase("p").add_step(StepEchoMessage("s", "", "")).add_step(StepEchoMessage("s", "", ""))
    )
    vr = create_validated_orchestrator(o)
    assert not vr.has_result()
    assert len(vr.report.errors) == 3
    assert len(vr.report.warnings) == 0
    assert len(vr.report.infos) == 0
