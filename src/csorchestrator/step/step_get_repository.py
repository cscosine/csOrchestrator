from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TypeVar

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.utils.file_system.path import is_clean_relative_path, resolve_path
from csorchestrator.utils.git.repo_clone_checkout import try_git_clone_checkout
from csorchestrator.utils.git.repo_validate_and_sync import validate_and_sync_repo


# base class for extra information that can be provided
class StepGetRepositoryExtra:
    pass


T = TypeVar("T", bound="StepGetRepositoryExtra")


@dataclass
class StepGetRepositoryExtraAccessToken(StepGetRepositoryExtra):
    token_name: str


class RepositoryType(Enum):
    GIT = 1


@dataclass
class StepGetRepository(StepBase):
    repo_type: RepositoryType
    repo_url: str
    repo_ref: str
    target_directory: str

    # note, repo_ref can be
    # - Branch, e.g. "main", "dev"
    # - Tag, e.g. "v0.0.1"
    # - Commit hash, e.g. "9f8e7d6c5b4a3210abcd1234ef56789012345678"

    _extras: dict[type, StepGetRepositoryExtra] = field(default_factory=dict)

    def resolved_target_directory_path(self) -> Path:
        return resolve_path(self.target_directory)

    def add_extra(
        self,
        extra: StepGetRepositoryExtra,
    ) -> "StepGetRepository":
        key = type(extra)
        self._extras[key] = extra
        return self

    def get_extra(self, t: type[T]) -> T | None:
        extra = self._extras.get(t)
        return extra if isinstance(extra, t) else None


def execute_step_get_repository(step: StepGetRepository, context: ContextLocalExecution) -> Report:
    if step.repo_type == RepositoryType.GIT:
        return _execute_step_get_repository_git(step, context)
    else:
        return Report().append_error(f"Unknown repository type {step.repo_type}")


def validate_step_get_repository(step: StepGetRepository) -> Report:
    report = Report()

    if not is_clean_relative_path(step.target_directory, avoid_leaving_base=True):
        report.append_error(
            f"Invalid target_directory {step.target_directory}, it must be a clean relative path that "
            "does not leave the base folder"
        )

    return report


def _execute_step_get_repository_git(repo_step: StepGetRepository, context: ContextLocalExecution) -> Report:
    assert repo_step.repo_type == RepositoryType.GIT  # defensive

    report = Report()

    target_full_path = context.base_folder_path / repo_step.target_directory

    if not target_full_path.is_dir():
        depth_one = StepGetRepositoryExtraDepthOne.has_depth_one_on_local_checkout(repo_step)

        report.append_info(
            f"Clone from {repo_step.repo_url} to {target_full_path} {f'depth one? {depth_one}' if depth_one else ''}"
        )

        r_sub = try_git_clone_checkout(
            repo_url=repo_step.repo_url, repo_ref=repo_step.repo_ref, target_path=target_full_path, depth_one=depth_one
        )

        report.append_report(r_sub)

    else:
        report.append_info(
            f"Given target_directory exists, then try to update from {repo_step.repo_url} ref {repo_step.repo_ref}"
        )

        validate_and_sync_report = validate_and_sync_repo(
            repo_url=repo_step.repo_url, repo_ref=repo_step.repo_ref, target_path=target_full_path
        )
        report.append_report(validate_and_sync_report)

    return report


@dataclass
class StepGetRepositoryExtraDepthOne(StepGetRepositoryExtra):
    on_local_checkout: bool
    on_github_action_checkout: bool

    @classmethod
    def has_depth_one_on_local_checkout(cls, repo_step: StepGetRepository) -> bool:
        depth_one_only = False
        depth_one_extra_opt = repo_step.get_extra(StepGetRepositoryExtraDepthOne)
        if depth_one_extra_opt is not None:
            depth_one_only = depth_one_extra_opt.on_local_checkout
        return depth_one_only

    @classmethod
    def has_depth_one_on_github_action_checkout(cls, repo_step: StepGetRepository) -> bool:
        depth_one_only = False
        depth_one_extra_opt = repo_step.get_extra(StepGetRepositoryExtraDepthOne)
        if depth_one_extra_opt is not None:
            depth_one_only = depth_one_extra_opt.on_github_action_checkout
        return depth_one_only
