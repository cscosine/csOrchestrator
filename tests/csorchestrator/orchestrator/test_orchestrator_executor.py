from dataclasses import dataclass

import pytest
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.orchestrator_executor import OrchestratorExecutor
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorVisitorBase
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.orchestrator.validated_orchestrator import (
    create_validated_orchestrator,
)


@dataclass
class StepCustom1(StepBase):
    pass


@dataclass
class StepCustom2(StepBase):
    pass


DUMMY_UNHANDLED_ERROR = "DummyVisitor does not handle this step type"


class OrchestratorVisitorDummy(OrchestratorVisitorBase):
    def init_visit(self) -> None:
        pass

    def end_visit(self, visit_complete: bool) -> None:
        pass

    def begin_phase(self, phase: Phase) -> None:
        pass

    def end_phase(self, phase_complete: bool) -> None:
        pass

    def visit_step_base(self, step: StepBase) -> Report:
        raise NotImplementedError(DUMMY_UNHANDLED_ERROR)


def test_orchestrator_executor_invalid_visitor() -> None:
    o = Orchestrator()

    o.create_phase("p1").add_step(StepCustom1(name="p1s1", description="p1 step s1")).add_step(
        StepCustom2(name="p1s2", description="p1 step s2")
    )

    o.create_phase("p2").add_step(StepCustom1(name="p2s1", description="p2 step s1")).add_step(
        StepCustom2(name="p2s2", description="p2 step s2")
    )

    ovr = create_validated_orchestrator(o)

    assert ovr.has_result()

    e = OrchestratorExecutor(ovr.result())

    ovb = OrchestratorVisitorDummy()

    with pytest.raises(NotImplementedError) as exc_info:
        e.execute(ovb)

    assert str(exc_info.value) == DUMMY_UNHANDLED_ERROR


# ------------------------------------------------------------------------------------------------


@dataclass
class OrchestratorVisitorConcretePerType(OrchestratorVisitorBase):
    visit_init_count: int = 0
    visit_end_count: int = 0
    phase_init_count: int = 0
    phase_end_count: int = 0
    visited_steps_1: int = 0
    visited_steps_2: int = 0

    def init_visit(self) -> None:
        self.visit_init_count += 1

    def end_visit(self, visit_complete: bool) -> None:
        self.visit_end_count += 1

    def begin_phase(self, phase: Phase) -> None:
        self.phase_init_count += 1

    def end_phase(self, phase_complete: bool) -> None:
        self.phase_end_count += 1

    def visit_step_base(self, step: StepBase) -> Report:
        raise NotImplementedError(f"Unhandled step type: {type(step).__name__}")

    visit_step = OrchestratorVisitorBase.create_visit_dispatch()

    @visit_step.register
    def _(self, step: StepCustom1) -> Report:
        self.visited_steps_1 += 1
        return Report()

    @visit_step.register
    def _(self, step: StepCustom2) -> Report:
        self.visited_steps_2 += 1
        return Report()


def test_orchestrator_executor_valid_visitor() -> None:
    o = Orchestrator()

    o.create_phase("p1").add_step(StepCustom1(name="p1s1", description="p1 step s1")).add_step(
        StepCustom2(name="p1s2", description="p1 step s2")
    )

    o.create_phase("p2").add_step(StepCustom1(name="p2s1", description="p2 step s1")).add_step(
        StepCustom2(name="p2s2", description="p2 step s2")
    )

    ovr = create_validated_orchestrator(o)

    assert ovr.has_result()

    e = OrchestratorExecutor(ovr.result())

    ovb = OrchestratorVisitorConcretePerType()

    e.execute(ovb)

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1

    assert ovb.phase_init_count == 2
    assert ovb.phase_end_count == 2

    assert ovb.visited_steps_1 == 2
    assert ovb.visited_steps_2 == 2


# ------------------------------------------------------------------------------------------------


@dataclass
class OrchestratorVisitorConcreteBaseOnly(OrchestratorVisitorBase):
    visit_init_count: int = 0
    visit_end_count: int = 0
    phase_init_count: int = 0
    phase_end_count: int = 0
    visited_steps: int = 0

    def init_visit(self) -> None:
        self.visit_init_count += 1

    def end_visit(self, visit_complete: bool) -> None:
        self.visit_end_count += 1

    def begin_phase(self, phase: Phase) -> None:
        self.phase_init_count += 1

    def end_phase(self, phase_complete: bool) -> None:
        self.phase_end_count += 1

    def visit_step_base(self, step: StepBase) -> Report:
        self.visited_steps += 1
        return Report()


def test_orchestrator_executor_base_only_visitor() -> None:
    o = Orchestrator()

    o.create_phase("p1").add_step(StepCustom1(name="p1s1", description="p1 step s1")).add_step(
        StepCustom2(name="p1s2", description="p1 step s2")
    )

    o.create_phase("p2").add_step(StepCustom1(name="p2s1", description="p2 step s1")).add_step(
        StepCustom2(name="p2s2", description="p2 step s2")
    )

    ovr = create_validated_orchestrator(o)

    assert ovr.has_result()

    e = OrchestratorExecutor(ovr.result())

    ovb = OrchestratorVisitorConcreteBaseOnly()

    e.execute(ovb)

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1

    assert ovb.phase_init_count == 2
    assert ovb.phase_end_count == 2

    assert ovb.visited_steps == 4


# ------------------------------------------------------------------------------------------------


@dataclass
class OrchestratorVisitorConcreteUseVisitBase(OrchestratorVisitorBase):
    visit_init_count: int = 0
    visit_end_count: int = 0
    phase_init_count: int = 0
    phase_end_count: int = 0
    visited_steps: int = 0

    def init_visit(self) -> None:
        self.visit_init_count += 1

    def end_visit(self, visit_complete: bool) -> None:
        self.visit_end_count += 1

    def begin_phase(self, phase: Phase) -> None:
        self.phase_init_count += 1

    def end_phase(self, phase_complete: bool) -> None:
        self.phase_end_count += 1

    def visit_step_base(self, step: StepBase) -> Report:
        self.visited_steps += 1
        return Report()

    # create the visit dispatch but do not register any handler, so all steps fall through to visit_step_base
    visit_step = OrchestratorVisitorBase.create_visit_dispatch()


def test_orchestrator_executor_base_only_visitor_use_visit_step_base() -> None:
    o = Orchestrator()

    o.create_phase("p1").add_step(StepCustom1(name="p1s1", description="p1 step s1")).add_step(
        StepCustom2(name="p1s2", description="p1 step s2")
    )

    o.create_phase("p2").add_step(StepCustom1(name="p2s1", description="p2 step s1")).add_step(
        StepCustom2(name="p2s2", description="p2 step s2")
    )

    ovr = create_validated_orchestrator(o)

    assert ovr.has_result()

    e = OrchestratorExecutor(ovr.result())

    ovb = OrchestratorVisitorConcreteUseVisitBase()

    e.execute(ovb)

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1

    assert ovb.phase_init_count == 2
    assert ovb.phase_end_count == 2

    assert ovb.visited_steps == 4


# ------------------------------------------------------------------------------------------------


@dataclass
class OrchestratorVisitorFailStep(OrchestratorVisitorBase):
    failing_step: int

    visit_init_count: int = 0
    visit_end_count: int = 0
    visit_complete: bool = False

    phase_init_count: int = 0
    phase_end_count: int = 0
    phase_complete: bool = False

    visited_steps: int = 0

    def init_visit(self) -> None:
        self.visit_init_count += 1

    def end_visit(self, visit_complete: bool) -> None:
        self.visit_end_count += 1
        self.visit_complete = visit_complete

    def begin_phase(self, phase: Phase) -> None:
        self.phase_init_count += 1

    def end_phase(self, phase_complete: bool) -> None:
        self.phase_complete = phase_complete
        self.phase_end_count += 1

    def visit_step_base(self, step: StepBase) -> Report:
        r = Report()
        if self.failing_step == self.visited_steps:
            r.errors.append("FAIL")
        self.visited_steps += 1
        return r

    # create the visit dispatch but do not register any handler, so all steps fall through to visit_step_base
    visit_step = OrchestratorVisitorBase.create_visit_dispatch()


def test_orchestrator_executor_base_fail_step() -> None:
    o = Orchestrator()

    o.create_phase("p1").add_step(StepCustom1(name="p1s1", description="p1 step s1")).add_step(
        StepCustom2(name="p1s2", description="p1 step s2")
    )

    o.create_phase("p2").add_step(StepCustom1(name="p2s1", description="p2 step s1")).add_step(
        StepCustom2(name="p2s2", description="p2 step s2")
    )

    ovr = create_validated_orchestrator(o)

    assert ovr.has_result()

    e = OrchestratorExecutor(ovr.result())

    # complete case
    ovb = OrchestratorVisitorFailStep(-1)

    e.execute(ovb)

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1
    assert ovb.visit_complete

    assert ovb.phase_init_count == 2
    assert ovb.phase_end_count == 2
    assert ovb.phase_complete

    assert ovb.visited_steps == 4

    # fail
    ovb = OrchestratorVisitorFailStep(0)

    e.execute(ovb)

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1
    assert not ovb.visit_complete

    assert ovb.phase_init_count == 1
    assert ovb.phase_end_count == 1
    assert not ovb.phase_complete

    assert ovb.visited_steps == 1

    ovb = OrchestratorVisitorFailStep(1)

    e.execute(ovb)

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1
    assert not ovb.visit_complete

    assert ovb.phase_init_count == 1
    assert ovb.phase_end_count == 1
    assert not ovb.phase_complete

    assert ovb.visited_steps == 2

    ovb = OrchestratorVisitorFailStep(2)

    e.execute(ovb)

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1
    assert not ovb.visit_complete

    assert ovb.phase_init_count == 2
    assert ovb.phase_end_count == 2
    assert not ovb.phase_complete

    assert ovb.visited_steps == 3

    ovb = OrchestratorVisitorFailStep(3)

    e.execute(ovb)

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1
    assert not ovb.visit_complete

    assert ovb.phase_init_count == 2
    assert ovb.phase_end_count == 2
    assert not ovb.phase_complete

    assert ovb.visited_steps == 4
