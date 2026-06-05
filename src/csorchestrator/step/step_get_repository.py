from dataclasses import dataclass, field
from pathlib import Path

from csorchestrator.ci.github.github_workflow_config import (
    JobOrchestratorMatrixExecution,
    StepCheckoutRepository,
    StepCheckoutRepositoryWith,
)
from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.orchestrator.step_base import StepBase, StepExtra
from csorchestrator.utils.file_system.path import is_clean_relative_path, resolve_path
from csorchestrator.utils.git.repo_clone_checkout import try_git_clone_checkout
from csorchestrator.utils.git.repo_validate_and_sync import validate_and_sync_repo


@dataclass(frozen=True)
class RepoUrlParts:
    repo_base_url: str
    repo_org: str
    repo_name: str

    def repo_org_name_sub_url(self) -> str:
        return self.repo_org + "/" + self.repo_name

    def repo_url(self) -> str:
        return self.repo_base_url + self.repo_org_name_sub_url()


@dataclass
class StepGetRepositoryGitHub(StepBase):
    repo_url_parts: RepoUrlParts
    repo_ref: str
    target_directory: str

    def repo_url(self) -> str:
        return self.repo_url_parts.repo_url()

    GITHUB_BASE_URL_SSH: str = "git@github.com:"
    GITHUB_BASE_URL_HTTPS: str = "https://github.com/"

    # note, repo_ref can be
    # - Branch, e.g. "main", "dev"
    # - Tag, e.g. "v0.0.1"
    # - Commit hash, e.g. "9f8e7d6c5b4a3210abcd1234ef56789012345678"

    def resolved_target_directory_path(self) -> Path:
        return resolve_path(self.target_directory)


@dataclass
class StepGetRepositoryExtraAccessToken(StepExtra):
    token_name: str

    @classmethod
    def get_token_name_or_none(cls, repo_step: StepGetRepositoryGitHub) -> str | None:
        access_token_extra = repo_step.get_extra(StepGetRepositoryExtraAccessToken)
        if access_token_extra is None:
            return None

        return access_token_extra.token_name


def execute_step_get_repository(
    repo_step: StepGetRepositoryGitHub, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    target_full_path = context.base_folder_path / repo_step.target_directory

    if not target_full_path.is_dir():
        depth_one = StepGetRepositoryExtraDepthOne.has_depth_one_on_local_checkout(repo_step)

        report.append_info(
            f"Clone from {repo_step.repo_url()} to {target_full_path} {f'depth one? {depth_one}' if depth_one else ''}"
        )

        r_sub = try_git_clone_checkout(
            repo_url=repo_step.repo_url(),
            repo_ref=repo_step.repo_ref,
            target_path=target_full_path,
            depth_one=depth_one,
        )

        report.append_report(r_sub)

    else:
        report.append_info(
            f"Given target_directory exists, then try to update from {repo_step.repo_url()} ref {repo_step.repo_ref}"
        )

        validate_and_sync_report = validate_and_sync_repo(
            repo_url=repo_step.repo_url(), repo_ref=repo_step.repo_ref, target_path=target_full_path
        )
        report.append_report(validate_and_sync_report)

    return report


def step_get_repository_to_githubwf(
    step: StepGetRepositoryGitHub, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:
    wf_job.steps.append(
        StepCheckoutRepository(
            name=step.name,
            with_step=StepCheckoutRepositoryWith(
                repository=step.repo_url_parts.repo_org_name_sub_url(),
                path=step.target_directory,
                ref=step.repo_ref,
                fetch_depth="1"
                if StepGetRepositoryExtraDepthOne.has_depth_one_on_github_action_checkout(step)
                else None,
                token=StepGetRepositoryExtraAccessToken.get_token_name_or_none(step),
            ),
        )
    )
    return Report()


def validate_step_get_repository(step: StepGetRepositoryGitHub) -> Report:
    report = Report()

    if not is_clean_relative_path(step.target_directory, avoid_leaving_base=True):
        report.append_error(
            f"Invalid target_directory {step.target_directory}, it must be a clean relative path that "
            "does not leave the base folder"
        )

    return report


@dataclass
class StepGetRepositoryValidator:
    _collected_step_get_repository_target_directories: set[Path] = field(default_factory=set)

    def clear(self) -> None:
        self._collected_step_get_repository_target_directories.clear()

    def validate_step_get_repository(self, step: StepGetRepositoryGitHub) -> Report:
        r = validate_step_get_repository(step)
        if not r.has_errors():
            target_directory_path = step.resolved_target_directory_path()
            if target_directory_path in self._collected_step_get_repository_target_directories:
                r.append_error(f"target_directory {str(target_directory_path)} is already used by another step")
            else:
                self._collected_step_get_repository_target_directories.add(target_directory_path)
        return r


@dataclass
class StepGetRepositoryExtraDepthOne(StepExtra):
    on_local_checkout: bool
    on_github_action_checkout: bool

    @classmethod
    def has_depth_one_on_local_checkout(cls, repo_step: StepGetRepositoryGitHub) -> bool:
        depth_one_only = False
        depth_one_extra_opt = repo_step.get_extra(StepGetRepositoryExtraDepthOne)
        if depth_one_extra_opt is not None:
            depth_one_only = depth_one_extra_opt.on_local_checkout
        return depth_one_only

    @classmethod
    def has_depth_one_on_github_action_checkout(cls, repo_step: StepGetRepositoryGitHub) -> bool:
        depth_one_only = False
        depth_one_extra_opt = repo_step.get_extra(StepGetRepositoryExtraDepthOne)
        if depth_one_extra_opt is not None:
            depth_one_only = depth_one_extra_opt.on_github_action_checkout
        return depth_one_only
