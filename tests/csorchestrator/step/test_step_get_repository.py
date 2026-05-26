from dataclasses import dataclass
from pathlib import Path

import pytest

from csorchestrator.orchestrator.execution import create_context_local_execution
from csorchestrator.orchestrator.step_base import StepExtra
from csorchestrator.reporters.reporter_sink_dummy import ReporterSinkDummy
from csorchestrator.step.step_get_repository import (
    RepositoryType,
    StepGetRepository,
    StepGetRepositoryExtraAccessToken,
    StepGetRepositoryExtraDepthOne,
    execute_step_get_repository,
    validate_step_get_repository,
)
from tests.csorchestrator.repo_test_data_config import RepoTestData


@dataclass
class StepGetRepositoryExtraCustom(StepExtra):
    value: int


@dataclass
class StepGetRepositoryExtraNotUsed(StepExtra):
    pass


def test_step_get_repository():
    s = StepGetRepository(
        repo_type=RepositoryType.GIT,
        name="get repo",
        description="get repo desc",
        target_directory="dir",
        repo_url="url://test.git",
        repo_ref="main",
    )
    s.add_extra(StepGetRepositoryExtraAccessToken(token_name="THE_TOKEN")).add_extra(StepGetRepositoryExtraCustom(25))

    assert s.get_extra(StepExtra) is None
    assert s.get_extra(StepGetRepositoryExtraNotUsed) is None

    token_extra = s.get_extra(StepGetRepositoryExtraAccessToken)
    assert token_extra is not None
    assert token_extra.token_name == "THE_TOKEN"

    custom_extra = s.get_extra(StepGetRepositoryExtraCustom)
    assert custom_extra is not None
    assert custom_extra.value == 25

    # substitute
    s.add_extra(StepGetRepositoryExtraCustom(52))
    custom_extra = s.get_extra(StepGetRepositoryExtraCustom)
    assert custom_extra is not None
    assert custom_extra.value == 52


def test_validate_step_get_repository() -> None:
    s = StepGetRepository(
        repo_type=RepositoryType.GIT,
        name="get repo",
        description="get repo desc",
        target_directory="../dir",
        repo_url="url://test.git",
        repo_ref="main",
    )

    report = validate_step_get_repository(s)
    assert report.has_errors()
    assert "Invalid target_directory" in report.errors[0]

    s.target_directory = "dir"
    report = validate_step_get_repository(s)
    assert not report.has_errors()


def test_resolved_target_directory_path() -> None:
    s = StepGetRepository(
        repo_type=RepositoryType.GIT,
        name="get repo",
        description="get repo desc",
        target_directory="dir/subdir/..",
        repo_url="url://test.git",
        repo_ref="main",
    )

    target_directory_path = s.resolved_target_directory_path()
    assert str(target_directory_path.name) == "dir"


def test_step_get_repository_extra_depth_one() -> None:
    s = StepGetRepository(
        repo_type=RepositoryType.GIT,
        name="get repo",
        description="get repo desc",
        target_directory="dir/subdir/..",
        repo_url="url://test.git",
        repo_ref="main",
    )

    assert not StepGetRepositoryExtraDepthOne.has_depth_one_on_local_checkout(s)
    assert not StepGetRepositoryExtraDepthOne.has_depth_one_on_github_action_checkout(s)

    s.add_extra(StepGetRepositoryExtraDepthOne(on_local_checkout=False, on_github_action_checkout=False))
    assert not StepGetRepositoryExtraDepthOne.has_depth_one_on_local_checkout(s)
    assert not StepGetRepositoryExtraDepthOne.has_depth_one_on_github_action_checkout(s)

    s.add_extra(StepGetRepositoryExtraDepthOne(on_local_checkout=True, on_github_action_checkout=False))
    assert StepGetRepositoryExtraDepthOne.has_depth_one_on_local_checkout(s)
    assert not StepGetRepositoryExtraDepthOne.has_depth_one_on_github_action_checkout(s)

    s.add_extra(StepGetRepositoryExtraDepthOne(on_local_checkout=False, on_github_action_checkout=True))
    assert not StepGetRepositoryExtraDepthOne.has_depth_one_on_local_checkout(s)
    assert StepGetRepositoryExtraDepthOne.has_depth_one_on_github_action_checkout(s)

    s.add_extra(StepGetRepositoryExtraDepthOne(on_local_checkout=True, on_github_action_checkout=True))
    assert StepGetRepositoryExtraDepthOne.has_depth_one_on_local_checkout(s)
    assert StepGetRepositoryExtraDepthOne.has_depth_one_on_github_action_checkout(s)


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
@pytest.mark.parametrize(
    "repo_ref",
    [RepoTestData().main_branch, RepoTestData().dev_branch, RepoTestData().initial_commit_sha, RepoTestData().tag],
)
def test_execute_step_get_repository_success(tmp_path: Path, repo_url: str, depth_one: bool, repo_ref: str) -> None:
    cfg = RepoTestData()

    step = StepGetRepository(
        repo_type=RepositoryType.GIT,
        name="get test repo",
        description="get test repo desc",
        target_directory=cfg.destination_folder,
        repo_url=repo_url,
        repo_ref=repo_ref,
    )

    if depth_one:
        step.add_extra(StepGetRepositoryExtraDepthOne(on_local_checkout=True, on_github_action_checkout=True))

    contextOpt = create_context_local_execution(base_folder_path=str(tmp_path))
    assert contextOpt.result is not None
    context = contextOpt.result

    # execute the step for the first time, to clone the repo
    report = execute_step_get_repository(
        step=step,
        context=context,
        reporter_sink=ReporterSinkDummy(),
    )

    assert not report.has_errors()
    assert report.has_info()
    assert "Clone from" in report.infos[0]

    # Verify actual disk state
    target_path = tmp_path / cfg.destination_folder
    status_file = target_path / cfg.file_to_verify
    assert status_file.exists(), f"File {cfg.file_to_verify} not found in cloned repo"

    expected_content = {
        cfg.main_branch: cfg.expected_content_main,
        cfg.dev_branch: cfg.expected_content_dev,
        cfg.initial_commit_sha: cfg.expected_content_initial,
        cfg.tag: cfg.expected_content_tag,
    }.get(repo_ref)
    assert status_file.read_text(encoding="utf-8").strip() == expected_content

    # and get a second time, to test the "update" logic
    report = execute_step_get_repository(
        step=step,
        context=context,
        reporter_sink=ReporterSinkDummy(),
    )

    assert not report.has_errors()
    assert report.has_info()
    assert "Given target_directory exists, then try to update from" in report.infos[0]
    assert status_file.exists()
    assert status_file.read_text(encoding="utf-8").strip() == expected_content


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_execute_step_get_repository_update_fails(tmp_path: Path, repo_url: str, depth_one: bool) -> None:
    cfg = RepoTestData()

    step = StepGetRepository(
        repo_type=RepositoryType.GIT,
        name="get test repo",
        description="get test repo desc",
        target_directory=cfg.destination_folder,
        repo_url=repo_url,
        repo_ref=cfg.main_branch,
    )

    if depth_one:
        step.add_extra(StepGetRepositoryExtraDepthOne(on_local_checkout=True, on_github_action_checkout=True))

    contextOpt = create_context_local_execution(base_folder_path=str(tmp_path))
    assert contextOpt.result is not None
    context = contextOpt.result

    # execute the step for the first time, to clone the repo
    report = execute_step_get_repository(
        step=step,
        context=context,
        reporter_sink=ReporterSinkDummy(),
    )

    assert not report.has_errors()
    assert report.has_info()
    assert "Clone from" in report.infos[0]

    # and get a second time, to test the "update" logic and that it correctly detect errors
    step.repo_ref = cfg.dev_branch
    report = execute_step_get_repository(
        step=step,
        context=context,
        reporter_sink=ReporterSinkDummy(),
    )

    assert report.has_errors()
    assert report.has_info()
    assert "Given target_directory exists, then try to update from" in report.infos[0]
    assert "Branch mismatch: local=main, expected=dev" in report.errors[0]


def test_execute_step_get_repository_unknown_repository_type(tmp_path: Path) -> None:
    step = StepGetRepository(
        repo_type="NOT_AN_EXISTING_TYPE",  # type: ignore
        name="get repo",
        description="get repo desc",
        target_directory="dir",
        repo_url="url://test.git",
        repo_ref="main",
    )
    context = create_context_local_execution(base_folder_path=str(tmp_path))
    assert context.result is not None

    report = execute_step_get_repository(step, context.result, reporter_sink=ReporterSinkDummy())

    assert report.has_errors()
    assert "Unknown repository type" in report.errors[0]
