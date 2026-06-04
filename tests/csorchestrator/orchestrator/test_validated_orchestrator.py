from csorchestrator.orchestrator.orchestrator import create_orchestrator_factory
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.validated_orchestrator import (
    create_validated_orchestrator,
)
from csorchestrator.step.step_echo_message import StepEchoMessage
from csorchestrator.step.step_get_repository import RepoUrlParts, StepGetRepositoryGitHub


def test_orchestrator_valid() -> None:
    # valid, no repetition in phases or step
    o = create_orchestrator_factory("myName", "0.0.0", "exec-job")
    o.add_phase(Phase("p1").add_step(StepEchoMessage("s1", "", "")).add_step(StepEchoMessage("s2", "", ""))).add_phase(
        Phase("p2").add_step(StepEchoMessage("s1", "", "")).add_step(StepEchoMessage("s2", "", ""))
    )
    vr = create_validated_orchestrator(o)
    assert vr.has_result()
    assert vr.result == o
    assert len(vr.report.errors) == 0
    assert len(vr.report.warnings) == 0
    assert len(vr.report.infos) == 0


def test_orchestrator_invalid_repeated_phase_names() -> None:
    # invalid, repetition in phases names
    o = create_orchestrator_factory("myName", "0.0.0", "exec-job")
    o.add_phase(Phase("p").add_step(StepEchoMessage("s1", "", ""))).add_phase(
        Phase("p").add_step(StepEchoMessage("s1", "", ""))
    )
    vr = create_validated_orchestrator(o)
    assert not vr.has_result()
    assert len(vr.report.errors) == 1
    assert len(vr.report.warnings) == 0
    assert len(vr.report.infos) == 0


def test_orchestrator_invalid_repeated_step_names() -> None:
    # invalid, repetition in step names
    o = create_orchestrator_factory("myName", "0.0.0", "exec-job")
    o.add_phase(Phase("p").add_step(StepEchoMessage("s", "", "")).add_step(StepEchoMessage("s", "", "")))
    vr = create_validated_orchestrator(o)
    assert not vr.has_result()
    assert len(vr.report.errors) == 1
    assert len(vr.report.warnings) == 0
    assert len(vr.report.infos) == 0


def test_orchestrator_invalid_repeated_phase_and_step_names() -> None:
    # invalid, repetition in both phases and step names
    o = create_orchestrator_factory("myName", "0.0.0", "exec-job")
    o.add_phase(Phase("p").add_step(StepEchoMessage("s", "", "")).add_step(StepEchoMessage("s", "", ""))).add_phase(
        Phase("p").add_step(StepEchoMessage("s", "", "")).add_step(StepEchoMessage("s", "", ""))
    )
    vr = create_validated_orchestrator(o)
    assert not vr.has_result()
    assert len(vr.report.errors) == 3
    assert len(vr.report.warnings) == 0
    assert len(vr.report.infos) == 0


def test_orchestrator_invalid_step_get_repository() -> None:
    # invalid, step get repository with empty repository name
    o = create_orchestrator_factory("myName", "0.0.0", "exec-job")
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
    assert not vr.has_result()
    assert len(vr.report.errors) == 1
    assert "Invalid target_directory" in vr.report.errors[0]
    assert len(vr.report.warnings) == 0
    assert len(vr.report.infos) == 0


def test_orchestrator_invalid_step_duplicate_target_directory() -> None:
    # invalid, step get repository with duplicate target directory
    o = create_orchestrator_factory("myName", "0.0.0", "exec-job")
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

    assert not vr.has_result()
    assert len(vr.report.errors) == 1
    assert "already used by another step" in vr.report.errors[0]
