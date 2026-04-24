from dataclasses import dataclass

from csorchestrator.step.step_get_repository import (
    RepositoryType,
    StepGetRepository,
    StepGetRepositoryExtra,
    StepGetRepositoryExtraAccessToken,
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

    assert s.get_extra(StepGetRepositoryExtraAccessToken).token_name == "THE_TOKEN"
    assert s.get_extra(StepGetRepositoryExtraCustom).value == 25

    # substitute
    s.add_extra(StepGetRepositoryExtraCustom(52))
    assert s.get_extra(StepGetRepositoryExtraCustom).value == 52
