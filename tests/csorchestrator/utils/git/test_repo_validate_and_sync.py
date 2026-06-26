import logging
import shutil
from pathlib import Path

import git
import pytest
from git import GitCommandError, Repo

from csorchestrator.foundation.git.repo_clone_checkout import try_git_clone_checkout
from csorchestrator.foundation.git.repo_validate_and_sync import validate_and_sync_repo
from csorchestrator.foundation.git.resolve_url import RepoUrlParts
from tests.csorchestrator.repo_test_data_config import RepoTestData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO this function has been added in multiple places, factorize
def _clone_test_repo(target_path: Path, repo_url: RepoUrlParts, repo_ref: str, depth_one: bool) -> None:
    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url.repo_url(), repo_ref=repo_ref, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_main_branch_no_changes_succeed(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=depth_one)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_tag_no_changes_succeed(tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.tag, depth_one=depth_one)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.tag, target_path=target_path)
    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_commit_no_changes_succeed(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.initial_commit_sha, depth_one=depth_one)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.initial_commit_sha, target_path=target_path)
    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_clone_remote_fails(tmp_path: Path, repo_url: RepoUrlParts) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=False)

    r = validate_and_sync_repo(repo_url.repo_url(), "wrong-ref", target_path=target_path)
    assert r.has_errors()
    assert "Git operation failed" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_clone_tag_commit_mismatch(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.tag, depth_one=depth_one)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.initial_commit_sha, target_path=target_path)
    assert r.has_errors()
    assert "commit mismatch" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_clone_commit_tag_mismatch(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.initial_commit_sha, depth_one=depth_one)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.tag, target_path=target_path)
    assert r.has_errors()
    assert "tag mismatch" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_main_branch_dirty_edit(tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=depth_one)

    with open(target_path / cfg.file_to_verify, "w", encoding="utf-8") as f:
        f.write("Hello, world!")

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "Repository has uncommitted or untracked changes" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_main_branch_dirty_new_file(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=depth_one)

    with open(target_path / "NEWFILE.txt", "w", encoding="utf-8") as f:
        f.write("Hello, world!")

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "Repository has uncommitted or untracked changes" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_main_branch_no_remote_fail(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=depth_one)

    repo = Repo(target_path)
    for remote in list(repo.remotes):
        repo.delete_remote(remote)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "Failed to read remote URL" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_main_branch_no_refs_fail(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=depth_one)

    # remove the refs files

    git_dir = Path(target_path) / ".git"

    shutil.rmtree(git_dir / "refs", ignore_errors=True)

    head_file = git_dir / "HEAD"
    if head_file.exists():
        head_file.unlink()

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "is not a valid git repository" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_bare_fails(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    if not depth_one:
        repo = Repo.clone_from(repo_url.repo_url(), target_path, bare=True)
    else:
        repo = Repo.clone_from(repo_url.repo_url(), target_path, no_checkout=True, bare=True)

        remote = repo.remotes[0].name
        repo.git.fetch("--depth", "1", remote, cfg.main_branch)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "Repository is bare" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_main_branch_wrong_local_url(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=depth_one)

    # change the remote URL to something else
    repo = Repo(target_path)
    repo.delete_remote(repo.remotes[0])
    repo.create_remote("origin", "https://example.com/other/repo.git")

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "Remote URL mismatch" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_main_branch_mismatch(tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=depth_one)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.dev_branch, target_path=target_path)
    assert r.has_errors()
    assert "Branch mismatch" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_main_branch_fail_pull_ff(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=depth_one)

    repo = Repo(target_path)
    # Set local config
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "Test User")
        cw.set_value("user", "email", "test@example.com")
    repo.git.commit("--amend", "-m", "New commit message")

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "Failed to pull local repo" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_main_branch_fail_fetch_ff(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=depth_one)

    target_path_str = str(target_path)

    def raise_fetch(self, *args, **kwargs):
        if str(self.working_dir) == target_path_str:
            raise GitCommandError("fetch", "fetch failed")
        return git.cmd.Git.__getattr__(self, "fetch")(*args, **kwargs)

    monkeypatch.setattr(git.cmd.Git, "fetch", raise_fetch, raising=False)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "Failed to fetch local repo" in r.errors[0]


# coverage for defensive code in case of unknown ref type, which should never happen but let's be defensive anyway
@pytest.mark.slow
@pytest.mark.git
@pytest.mark.parametrize("depth_one", [True, False])
def test_validate_and_sync_repo_unknown_ref_type(
    tmp_path: Path, repo_url: RepoUrlParts, depth_one: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=depth_one)

    from csorchestrator.foundation.git import repo_validate_and_sync as mod

    def mock_resolve_ref_type(repo, ref):
        return "unknown_ref_type"

    monkeypatch.setattr(mod, "resolve_ref_type", mock_resolve_ref_type)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "Unknown ref type for temporary cloned repo " in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_detached_head(tmp_path: Path, repo_url: RepoUrlParts) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_test_repo(target_path=target_path, repo_url=repo_url, repo_ref=cfg.main_branch, depth_one=False)

    # Checkout to a commit to get detached HEAD
    repo = Repo(target_path)
    repo.git.checkout(cfg.initial_commit_sha)

    r = validate_and_sync_repo(repo_url.repo_url(), cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "Detached HEAD, expected a branch" in r.errors[0]
