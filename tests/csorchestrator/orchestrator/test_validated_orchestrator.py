from dataclasses import dataclass

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.core.report import Report
from csorchestrator.execution.factory import create_orchestrator_factory_all_supported_cases
from csorchestrator.execution.validated_orchestrator import (
    create_validated_orchestrator,
)
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import (
    JobOrchestratorMatrixExecution,
    StepBase,
    StepValidatorBase,
    StepValidatorNoOp,
)
from csorchestrator.step.step_get_repository import StepGetRepositoryGitHub
from csorchestrator.utils.git.resolve_url import RepoUrlParts


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


def test_orchestrator_valid() -> None:
    # valid, no repetition in phases or step
    o = create_orchestrator_factory_all_supported_cases("myName", "0.0.0", "exec-job")

    o.add_phase(Phase("p1").add_step(StepEchoMessage("s1", "", "")).add_step(StepEchoMessage("s2", "", ""))).add_phase(
        Phase("p2").add_step(StepEchoMessage("s1", "", "")).add_step(StepEchoMessage("s2", "", ""))
    )

    vr = create_validated_orchestrator(o)
    assert vr.orchestrator is not None
    assert vr.orchestrator == o
    assert not vr.has_any_error()


def test_orchestrator_invalid_repeated_phase_names() -> None:
    # invalid, repetition in phases names
    o = create_orchestrator_factory_all_supported_cases("myName", "0.0.0", "exec-job")
    o.add_phase(Phase("p").add_step(StepEchoMessage("s1", "", ""))).add_phase(
        Phase("p").add_step(StepEchoMessage("s1", "", ""))
    )
    vr = create_validated_orchestrator(o)
    assert vr.orchestrator is None
    assert vr.has_any_error()

    assert len(vr.main_report.errors) == 1
    assert len(vr.main_report.warnings) == 0
    assert len(vr.main_report.infos) == 0


def test_orchestrator_invalid_repeated_step_names() -> None:
    # invalid, repetition in step names
    o = create_orchestrator_factory_all_supported_cases("myName", "0.0.0", "exec-job")

    o.add_phase(Phase("p").add_step(StepEchoMessage("s", "", "")).add_step(StepEchoMessage("s", "", "")))
    vr = create_validated_orchestrator(o)
    assert vr.orchestrator is None
    assert vr.has_any_error()

    assert len(vr.main_report.errors) == 1
    assert len(vr.main_report.warnings) == 0
    assert len(vr.main_report.infos) == 0


def test_orchestrator_invalid_repeated_phase_and_step_names() -> None:
    # invalid, repetition in both phases and step names
    o = create_orchestrator_factory_all_supported_cases("myName", "0.0.0", "exec-job")

    o.add_phase(Phase("p").add_step(StepEchoMessage("s", "", "")).add_step(StepEchoMessage("s", "", ""))).add_phase(
        Phase("p").add_step(StepEchoMessage("s", "", "")).add_step(StepEchoMessage("s", "", ""))
    )
    vr = create_validated_orchestrator(o)
    assert vr.orchestrator is None
    assert vr.has_any_error()

    assert len(vr.main_report.errors) == 3
    assert len(vr.main_report.warnings) == 0
    assert len(vr.main_report.infos) == 0


def test_orchestrator_invalid_step_get_repository() -> None:
    # invalid, step get repository with empty repository name
    o = create_orchestrator_factory_all_supported_cases("myName", "0.0.0", "exec-job")

    s = StepGetRepositoryGitHub(
        name="get repo",
        description="get repo desc",
        target_directory="../dir",
        repo_url_parts=RepoUrlParts(
            StepGetRepositoryGitHub.GITHUB_BASE_URL_SSH,
            repo_org="cscosine",
            repo_name="myrepo",
        ),
        repo_ref="main",
    )
    o.add_phase(Phase("p").add_step(s))
    vr = create_validated_orchestrator(o)
    assert vr.orchestrator is None
    assert vr.has_any_error()

    assert len(vr.main_report.errors) == 0
    assert len(vr.main_report.warnings) == 0
    assert len(vr.main_report.infos) == 0
    assert len(vr.validation_reports) == 1  # 1 phase
    assert len(vr.validation_reports[0]) == 1  # 1 step
    assert "Invalid target_directory" in vr.validation_reports[0][0].errors[0]


def test_orchestrator_invalid_step_duplicate_target_directory() -> None:
    # invalid, step get repository with duplicate target directory
    o = create_orchestrator_factory_all_supported_cases("myName", "0.0.0", "exec-job")

    s1 = StepGetRepositoryGitHub(
        name="get repo 1",
        description="get repo desc 1",
        target_directory="./dir",
        repo_url_parts=RepoUrlParts(
            StepGetRepositoryGitHub.GITHUB_BASE_URL_SSH,
            repo_org="cscosine",
            repo_name="myrepo",
        ),
        repo_ref="main",
    )
    s2 = StepGetRepositoryGitHub(
        name="get repo 2",
        description="get repo desc 2",
        target_directory="dir",
        repo_url_parts=RepoUrlParts(
            StepGetRepositoryGitHub.GITHUB_BASE_URL_SSH,
            repo_org="cscosine",
            repo_name="myrepo",
        ),
        repo_ref="main",
    )
    o.add_phase(Phase("p").add_step(s1).add_step(s2))

    vr = create_validated_orchestrator(o)

    assert vr.orchestrator is None
    assert vr.has_any_error()

    assert len(vr.main_report.errors) == 0
    assert len(vr.main_report.warnings) == 0
    assert len(vr.main_report.infos) == 0
    assert len(vr.validation_reports) == 1  # 1 phase
    assert len(vr.validation_reports[0]) == 2  # 2 steps
    assert "already used by another step" in vr.validation_reports[0][1].errors[0]
