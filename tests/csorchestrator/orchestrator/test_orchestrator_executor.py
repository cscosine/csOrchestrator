from dataclasses import dataclass

import pytest

from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.orchestrator_executor import (
    execute_orchestrator,
    flatten_orchestrator_executor_visit_reports,
)
from csorchestrator.orchestrator.orchestrator_visitor_base import (
    OrchestratorExecutorVisitReports,
    OrchestratorVisitorBase,
)
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.orchestrator.validated_orchestrator import (
    create_validated_orchestrator,
)
from csorchestrator.reporters.orchestrator_executor_reporter_dummy import OrchestratorExecutorReporterDummy


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

    def visit_step_base(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        raise NotImplementedError(DUMMY_UNHANDLED_ERROR)


def test_orchestrator_executor_invalid_visitor() -> None:
    o = Orchestrator("myName")

    o.create_phase("p1").add_step(StepCustom1(name="p1s1", description="p1 step s1")).add_step(
        StepCustom2(name="p1s2", description="p1 step s2")
    )

    o.create_phase("p2").add_step(StepCustom1(name="p2s1", description="p2 step s1")).add_step(
        StepCustom2(name="p2s2", description="p2 step s2")
    )

    ovr = create_validated_orchestrator(o)

    assert ovr.has_result()
    orchestrator = ovr.result
    assert orchestrator is not None

    with pytest.raises(NotImplementedError) as exc_info:
        execute_orchestrator(orchestrator, OrchestratorVisitorDummy(), OrchestratorExecutorReporterDummy())

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

    def visit_step_base(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        raise NotImplementedError(f"Unhandled step type: {type(step).__name__}")

    visit_step = OrchestratorVisitorBase.create_visit_dispatch()

    @visit_step.register
    def _(self, step: StepCustom1, reporter_sink: ReporterSinkBase) -> Report:
        self.visited_steps_1 += 1
        return Report()

    @visit_step.register
    def _(self, step: StepCustom2, reporter_sink: ReporterSinkBase) -> Report:
        self.visited_steps_2 += 1
        return Report()


def test_orchestrator_executor_valid_visitor() -> None:
    o = Orchestrator("myName")

    o.create_phase("p1").add_step(StepCustom1(name="p1s1", description="p1 step s1")).add_step(
        StepCustom2(name="p1s2", description="p1 step s2")
    )

    o.create_phase("p2").add_step(StepCustom1(name="p2s1", description="p2 step s1")).add_step(
        StepCustom2(name="p2s2", description="p2 step s2")
    )

    ovr = create_validated_orchestrator(o)

    assert ovr.has_result()
    orchestrator = ovr.result
    assert orchestrator is not None

    ovb = OrchestratorVisitorConcretePerType()

    execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())

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

    def visit_step_base(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        self.visited_steps += 1
        return Report()


def test_orchestrator_executor_base_only_visitor() -> None:
    o = Orchestrator("myName")

    o.create_phase("p1").add_step(StepCustom1(name="p1s1", description="p1 step s1")).add_step(
        StepCustom2(name="p1s2", description="p1 step s2")
    )

    o.create_phase("p2").add_step(StepCustom1(name="p2s1", description="p2 step s1")).add_step(
        StepCustom2(name="p2s2", description="p2 step s2")
    )

    ovr = create_validated_orchestrator(o)

    assert ovr.has_result()
    orchestrator = ovr.result
    assert orchestrator is not None

    ovb = OrchestratorVisitorConcreteBaseOnly()

    execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())

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

    def visit_step_base(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        self.visited_steps += 1
        return Report()

    # create the visit dispatch but do not register any handler, so all steps fall through to visit_step_base
    visit_step = OrchestratorVisitorBase.create_visit_dispatch()


def test_orchestrator_executor_base_only_visitor_use_visit_step_base() -> None:
    o = Orchestrator("myName")

    o.create_phase("p1").add_step(StepCustom1(name="p1s1", description="p1 step s1")).add_step(
        StepCustom2(name="p1s2", description="p1 step s2")
    )

    o.create_phase("p2").add_step(StepCustom1(name="p2s1", description="p2 step s1")).add_step(
        StepCustom2(name="p2s2", description="p2 step s2")
    )

    ovr = create_validated_orchestrator(o)

    assert ovr.has_result()
    orchestrator = ovr.result
    assert orchestrator is not None

    ovb = OrchestratorVisitorConcreteUseVisitBase()

    execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())

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

    def visit_step_base(self, step: StepBase, reporter_sink: ReporterSinkBase) -> Report:
        r = Report()
        if self.failing_step == self.visited_steps:
            r.append_error("FAIL")
        self.visited_steps += 1
        return r

    # create the visit dispatch but do not register any handler, so all steps fall through to visit_step_base
    visit_step = OrchestratorVisitorBase.create_visit_dispatch()


def test_orchestrator_executor_base_fail_step() -> None:
    o = Orchestrator("myName")

    o.create_phase("p1").add_step(StepCustom1(name="p1s1", description="p1 step s1")).add_step(
        StepCustom2(name="p1s2", description="p1 step s2")
    )

    o.create_phase("p2").add_step(StepCustom1(name="p2s1", description="p2 step s1")).add_step(
        StepCustom2(name="p2s2", description="p2 step s2")
    )

    ovr = create_validated_orchestrator(o)

    assert ovr.has_result()
    orchestrator = ovr.result
    assert orchestrator is not None

    # complete case
    ovb = OrchestratorVisitorFailStep(-1)

    visit_reports = execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1
    assert ovb.visit_complete

    assert ovb.phase_init_count == 2
    assert ovb.phase_end_count == 2
    assert ovb.phase_complete

    assert ovb.visited_steps == 4

    assert len(visit_reports) == 2
    assert len(visit_reports[0]) == 2
    assert not visit_reports[0][0].has_errors()
    assert not visit_reports[0][1].has_errors()
    assert len(visit_reports[1]) == 2
    assert not visit_reports[1][0].has_errors()
    assert not visit_reports[1][1].has_errors()

    # fail
    ovb = OrchestratorVisitorFailStep(0)

    visit_reports = execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1
    assert not ovb.visit_complete

    assert ovb.phase_init_count == 1
    assert ovb.phase_end_count == 1
    assert not ovb.phase_complete

    assert ovb.visited_steps == 1

    assert len(visit_reports) == 1
    assert len(visit_reports[0]) == 1
    assert visit_reports[0][0].has_errors()

    ovb = OrchestratorVisitorFailStep(1)

    visit_reports = execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1
    assert not ovb.visit_complete

    assert ovb.phase_init_count == 1
    assert ovb.phase_end_count == 1
    assert not ovb.phase_complete

    assert ovb.visited_steps == 2

    assert len(visit_reports) == 1
    assert len(visit_reports[0]) == 2
    assert not visit_reports[0][0].has_errors()
    assert visit_reports[0][1].has_errors()

    ovb = OrchestratorVisitorFailStep(2)

    visit_reports = execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1
    assert not ovb.visit_complete

    assert ovb.phase_init_count == 2
    assert ovb.phase_end_count == 2
    assert not ovb.phase_complete

    assert ovb.visited_steps == 3

    assert len(visit_reports) == 2
    assert len(visit_reports[0]) == 2
    assert not visit_reports[0][0].has_errors()
    assert not visit_reports[0][1].has_errors()
    assert len(visit_reports[1]) == 1
    assert visit_reports[1][0].has_errors()

    ovb = OrchestratorVisitorFailStep(3)

    visit_reports = execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())

    assert ovb.visit_init_count == 1
    assert ovb.visit_end_count == 1
    assert not ovb.visit_complete

    assert ovb.phase_init_count == 2
    assert ovb.phase_end_count == 2
    assert not ovb.phase_complete

    assert ovb.visited_steps == 4

    assert len(visit_reports) == 2
    assert len(visit_reports[0]) == 2
    assert not visit_reports[0][0].has_errors()
    assert not visit_reports[0][1].has_errors()
    assert len(visit_reports[1]) == 2
    assert not visit_reports[1][0].has_errors()
    assert visit_reports[1][1].has_errors()


def test_flatten_orchestrator_executor_visit_reports() -> None:

    oevr: OrchestratorExecutorVisitReports = [
        [Report().append_warning("W"), Report().append_error("E")],
        [Report().append_error("E"), Report().append_info("I"), Report().append_warning("W")],
    ]

    rf = flatten_orchestrator_executor_visit_reports(oevr)

    assert rf.errors == ("E", "E")
    assert rf.warnings == ("W", "W")
    assert rf.infos == ("I",)
