import logging
import shutil
from pathlib import Path

import pytest
from git import Repo

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
