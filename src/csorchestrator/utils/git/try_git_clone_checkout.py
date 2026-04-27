from enum import Enum
from pathlib import Path

from git import GitCommandError, Repo

from csorchestrator.core.expected import Expected
from csorchestrator.core.report import Report


# -------------------------
# ENUM
# -------------------------
class RefKind(str, Enum):
    BRANCH = "branch"
    TAG = "tag"
    COMMIT = "commit"


def _report_git_command_error(report: Report, e: GitCommandError) -> None:
    report.append_error(
        "Git operation failed:\n"
        f"- Command: {e.command}\n"
        f"- Exit code: {getattr(e, 'status', None)}\n"
        f"- Error output: {e.stderr}\n"
    )


def _resolve_ref_type(repo: Repo, ref: str) -> Expected[RefKind, str]:

    # 1. BRANCH
    if ref in repo.heads:
        commit = repo.commit(ref)
        return Expected[RefKind, str].make_value(RefKind.BRANCH)

    # 2. TAG
    if ref in repo.tags:
        commit = repo.commit(ref)
        return Expected[RefKind, str].make_value(RefKind.TAG)

    # 3. COMMIT
    commit = repo.commit(ref)
    sha = commit.hexsha

    if ref == sha:
        return Expected[RefKind, str].make_value(RefKind.COMMIT)
    else:
        return Expected[RefKind, str].make_error(f"repo reference {ref} differs from expected {sha} commit")


def try_git_clone_checkout(repo_url: str, repo_ref: str, target_path: Path, depth_one: bool) -> Report:
    try:
        # -------------------------
        # CLONE
        # -------------------------
        if not depth_one:
            repo = Repo.clone_from(repo_url, target_path)
        else:
            repo = Repo.clone_from(repo_url, target_path, no_checkout=True)

            remote = repo.remotes[0].name
            repo.git.fetch("--depth", "1", remote, repo_ref)

        # -------------------------
        # CHECKOUT RAW REF
        # -------------------------
        repo.git.checkout(repo_ref)

        # -------------------------
        # TYPE-SAFE RESOLUTION
        # -------------------------
        ref_kind_expected = _resolve_ref_type(repo, repo_ref)
        if ref_kind_expected.error is not None:
            return Report().append_error(ref_kind_expected.error)

        return Report().append_info(f"Successfully cloned from {repo_url} to {target_path}")

    except GitCommandError as e:
        report = Report()
        _report_git_command_error(report, e)
        return report
