from dataclasses import dataclass

from csorchestrator.step.step_add_repository import (
    StepAddRepository,
    StepAddRepositoryExtra,
    StepAddRepositoryExtraAccessToken,
)


@dataclass
class StepAddRepositoryExtraCustom(StepAddRepositoryExtra):
    value: int


@dataclass
class StepAddRepositoryExtraNotUsed(StepAddRepositoryExtra):
    pass


def test_step_add_repository():
    s = StepAddRepository(
        name="get repo", description="get repo desc", target_directory="dir", repo_url="url://test.git", ref="main"
    )
    s.add_extra(StepAddRepositoryExtraAccessToken(token_name="THE_TOKEN")).add_extra(StepAddRepositoryExtraCustom(25))

    assert s.get_extra(StepAddRepositoryExtra) is None
    assert s.get_extra(StepAddRepositoryExtraNotUsed) is None

    assert s.get_extra(StepAddRepositoryExtraAccessToken).token_name == "THE_TOKEN"
    assert s.get_extra(StepAddRepositoryExtraCustom).value == 25

    # substitute
    s.add_extra(StepAddRepositoryExtraCustom(52))
    assert s.get_extra(StepAddRepositoryExtraCustom).value == 52
