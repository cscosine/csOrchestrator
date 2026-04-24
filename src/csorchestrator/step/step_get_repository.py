import os  # TODO remove / change
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Type, TypeVar

from git import GitCommandError, Repo

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.step_base import StepBase


# base class for extra information that can be provided
class StepGetRepositoryExtra:
    pass


@dataclass
class StepGetRepositoryExtraAccessToken(StepGetRepositoryExtra):
    token_name: str


T = TypeVar("T", bound="StepGetRepositoryExtra")


class RepositoryType(Enum):
    GIT = 1


@dataclass
class StepGetRepository(StepBase):
    repo_type: RepositoryType
    repo_url: str
    repo_ref: str
    target_directory: str

    _extras: Dict[type, StepGetRepositoryExtra] = field(default_factory=dict)

    def add_extra(
        self,
        extra: StepGetRepositoryExtra,
    ) -> "StepGetRepository":
        key = type(extra)
        self._extras[key] = extra
        return self

    def get_extra(self, t: Type[T]) -> Optional[T]:
        extra = self._extras.get(t)
        return extra if isinstance(extra, t) else None


def execute_step_get_repository(step: StepGetRepository, context: ContextLocalExecution) -> Report:
    if step.repo_type == RepositoryType.GIT:
        return _execute_step_get_repository_git(step, context)
    else:
        return Report().append_error(f"Unknown repository type {step.repo_type}")


def _report_git_command_error(report: Report, e: GitCommandError) -> None:
    report.append_error(
        "Git operation failed:\n"
        f"- Command: {e.command}\n"
        f"- Exit code: {getattr(e, 'status', None)}\n"
        f"- Error output: {e.stderr}\n"
    )


def _execute_step_get_repository_git(repo_step: StepGetRepository, context: ContextLocalExecution) -> Report:
    assert repo_step.repo_type == RepositoryType.GIT  # defensive

    report = Report()

    if not os.path.isdir(repo_step.target_directory):  # TODO how to manage local / abs path ?
        report.append_info(
            f"Given target_directory does not exists, "
            f"then clone from {repo_step.repo_url} to {repo_step.target_directory}"
        )
        try:
            repo = Repo.clone_from(repo_step.repo_url, repo_step.target_directory)
            repo.git.checkout(repo_step.repo_ref)  # works both for branch and tag
            report.append_info(f"Succesfully cloned from {repo_step.repo_url} to {repo_step.target_directory}")
        except GitCommandError as e:
            _report_git_command_error(report, e)

    else:
        report.append_info(
            f"Given target_directory exists, "
            f"then try pull fast-forward from {repo_step.repo_url} ref {repo_step.repo_ref}"
        )
        try:
            repo = Repo(repo_step.target_directory)
            git = repo.git
            branch = repo.active_branch
            remote = branch.tracking_branch().remote_name
            ref = branch.name

            if ref == repo_step.repo_ref:
                git.pull(remote, ref, ff_only=True)
                report.append_info(
                    f"Succesfully pull fast-forward from {repo_step.repo_url} "
                    f"to {repo_step.target_directory} at ref {ref}"
                )
            else:
                report.append_error(
                    f"Cannot pull fast-forward from {repo_step.repo_url} to {repo_step.target_directory}, "
                    f"active branch is {ref} instead of {repo_step.repo_ref}"
                )

        except GitCommandError as e:
            _report_git_command_error(report, e)

    return report
