from dataclasses import dataclass

from csorchestrator.step.step_get_repository import (
    RepositoryType,
    StepGetRepository,
    StepGetRepositoryExtra,
    StepGetRepositoryExtraAccessToken,
    StepGetRepositoryExtraDepthOne,
    validate_step_get_repository,
)


@dataclass
class StepGetRepositoryExtraCustom(StepGetRepositoryExtra):
    value: int


@dataclass
class StepGetRepositoryExtraNotUsed(StepGetRepositoryExtra):
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

    assert s.get_extra(StepGetRepositoryExtra) is None
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
