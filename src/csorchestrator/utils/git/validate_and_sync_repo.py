from pathlib import Path

from git import GitCommandError, Remote, Repo
from git.util import IterableList

from csorchestrator.core.report import Report
from csorchestrator.step.step_get_repository import StepGetRepository
from csorchestrator.utils.git.try_git_clone_checkout import RefKind, _resolve_ref_type

# -------------------------
# helpers
# -------------------------


def _get_current_ref(repo: Repo) -> tuple[str, str]:
    """
    Returns (ref_name, commit_sha)
    If detached HEAD, ref_name is commit SHA.
    """
    if repo.head.is_detached:
        sha = repo.head.commit.hexsha
        return sha, sha

    return repo.active_branch.name, repo.head.commit.hexsha


def _resolve_default_remote(repo: Repo) -> IterableList[Remote]:
    if len(repo.remotes) == 0:
        raise ValueError("no remotes configured")

    if "origin" in repo.remotes:
        return repo.remotes["origin"]

    return repo.remotes[0]


# -------------------------
# main logic
# -------------------------


def validate_and_sync_repo(step: StepGetRepository) -> Report:
    repo = Repo(Path(step.target_directory))

    # 0. dirty check (fail early)
    if repo.is_dirty(untracked_files=True):
        return Report().append_error("working tree is dirty (modified or untracked files present)")

    # 1. local state
    local_ref, local_commit = _get_current_ref(repo)

    local_kind = _resolve_ref_type(repo, local_ref)
    if local_kind.error is not None:
        return Report().append_error(local_kind.error)

    # 2. remote
    try:
        remote = _resolve_default_remote(repo)
    except ValueError as e:
        return Report().append_error(str(e))

    try:
        is_shallow = repo.git.rev_parse("--is-shallow-repository") == "true"
    except Exception as e:
        return Report().append_error(str(e))

    try:
        remote.fetch("--update-shallow")

        # direct branch reference on remote
        if step.repo_ref in remote.refs:
            remote_commit = remote.refs[step.repo_ref].commit.hexsha
        else:
            # fallback: tags or direct commit
            repo = remote.repo
            remote_commit = repo.commit(step.repo_ref).hexsha

    except Exception as e:
        return Report().append_error(f"remote resolution failed: {e}")

    # 3. ref consistency (name check)
    if local_kind.value != RefKind.COMMIT and local_ref != step.repo_ref:
        return Report().append_error(f"local ref '{local_ref}' != expected '{step.repo_ref}'")

    # -------------------------
    # 4. BRANCH logic
    # -------------------------
    if local_kind.value == RefKind.BRANCH:
        if local_commit != remote_commit:
            try:
                repo.git.checkout(step.repo_ref)

                if is_shallow:
                    # shallow repos may require deeper fetch for FF safety
                    try:
                        repo.git.fetch("--unshallow")
                    except GitCommandError:
                        pass  # not always supported

                repo.git.pull("--ff-only")

            except GitCommandError as e:
                return Report().append_error(f"fast-forward failed (shallow={is_shallow}): {e}")

        return Report().append_info("branch synced")

    # -------------------------
    # 5. TAG / COMMIT logic
    # -------------------------
    if local_kind.value in (RefKind.TAG, RefKind.COMMIT):
        # shallow repos may not have full object graph
        if is_shallow:
            try:
                remote.fetch("--depth=1", step.repo_ref)
            except Exception:
                pass

        if local_commit != remote_commit:
            return Report().append_error(
                f"{local_kind.value} mismatch (shallow={is_shallow}): local={local_commit}, remote={remote_commit}"
            )

        return Report().append_info(f"{local_kind.value} verified")

    return Report().append_error("unsupported ref type")
