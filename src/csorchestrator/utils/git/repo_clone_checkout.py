from enum import Enum
from pathlib import Path

from git import GitCommandError, Repo

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


def resolve_ref_type(repo: Repo, ref: str) -> RefKind:

    # 1. BRANCH
    if ref in repo.heads:
        return RefKind.BRANCH

    # 2. TAG
    if ref in repo.tags:
        return RefKind.TAG

    return RefKind.COMMIT


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
        ref_kind = resolve_ref_type(repo, repo_ref)

        # if tag or branch OK, if commit let's check
        if ref_kind == RefKind.BRANCH or ref_kind == RefKind.TAG:
            pass
        elif ref_kind == RefKind.COMMIT:
            commit = repo.commit(repo_ref)
            sha = commit.hexsha

            if repo_ref != sha:
                return Report().append_error(f"repo reference {repo_ref} differs from expected {sha} commit")
        else:
            # this should never happen, but let's be defensive
            return Report().append_error(f"Unknown ref type for {repo_ref}")

        return Report().append_info(f"Successfully cloned from {repo_url} ref {repo_ref} to {target_path}")

    except GitCommandError as e:
        report = Report()
        _report_git_command_error(report, e)
        return report
