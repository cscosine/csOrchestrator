import logging
import shutil
from pathlib import Path

import pytest
from git import Repo

from csorchestrator.utils.git.try_git_clone_checkout import try_git_clone_checkout
from csorchestrator.utils.git.validate_and_sync_repo import validate_and_sync_repo
from tests.csorchestrator.utils.git.conftest import RepoRuntimeConfig
from tests.csorchestrator.utils.git.repo_config import RepoTestData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _clone_main_clean(target_path: Path, repo_runtime_config: RepoRuntimeConfig, depth_one: bool) -> None:
    cfg = RepoTestData()

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url, repo_ref=cfg.main_branch, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()


def _clone_tag_clean(target_path: Path, repo_runtime_config: RepoRuntimeConfig, depth_one: bool) -> None:
    cfg = RepoTestData()

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url, repo_ref=cfg.tag, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()


def _clone_sha_clean(target_path: Path, repo_runtime_config: RepoRuntimeConfig, depth_one: bool) -> None:
    cfg = RepoTestData()

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.initial_commit_sha,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert not r.has_errors()


def _clone_dev_clean(target_path: Path, repo_runtime_config: RepoRuntimeConfig, depth_one: bool) -> None:
    cfg = RepoTestData()

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url, repo_ref=cfg.dev_branch, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_main_branch_no_changes_succeed(
    tmp_path: Path, repo_runtime_config: RepoRuntimeConfig
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_main_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=False)

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.main_branch, target_path=target_path)
    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_main_branch_no_changes_succeed_depth_one(
    tmp_path: Path, repo_runtime_config: RepoRuntimeConfig
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_main_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=True)

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.main_branch, target_path=target_path)
    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_main_branch_ff_succeed(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_main_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=False)

    repo = Repo(target_path)
    repo.git.reset("--hard", "HEAD~1")

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.main_branch, target_path=target_path)
    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_main_branch_ff_succeed_depth_one(
    tmp_path: Path, repo_runtime_config: RepoRuntimeConfig
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_main_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=True)

    repo = Repo(target_path)
    repo.git.fetch(deepen=1)

    # git reset --hard HEAD~1
    parent = repo.commit("HEAD").parents[0]
    repo.head.reset(commit=parent, index=True, working_tree=True)

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.main_branch, target_path=target_path)
    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_main_branch_dirty_edit(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_main_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=False)

    with open(target_path / cfg.file_to_verify, "w", encoding="utf-8") as f:
        f.write("Hello, world!")

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "working tree is dirty" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_main_branch_dirty_new_file(
    tmp_path: Path, repo_runtime_config: RepoRuntimeConfig
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_main_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=False)

    with open(target_path / "NEWFILE.txt", "w", encoding="utf-8") as f:
        f.write("Hello, world!")

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "working tree is dirty" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_main_branch_no_remote_fail(
    tmp_path: Path, repo_runtime_config: RepoRuntimeConfig
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_main_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=False)

    repo = Repo(target_path)
    for remote in list(repo.remotes):
        repo.delete_remote(remote)

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "has no remote" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_main_branch_no_refs_fail(
    tmp_path: Path, repo_runtime_config: RepoRuntimeConfig
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_main_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=False)

    # remove the refs files

    git_dir = Path(target_path) / ".git"

    shutil.rmtree(git_dir / "refs", ignore_errors=True)

    head_file = git_dir / "HEAD"
    if head_file.exists():
        head_file.unlink()

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "InvalidGitRepositoryError" in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_ref_differs(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_main_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=False)

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.head, target_path=target_path)
    assert r.has_errors()
    assert "local ref 'main' != expected " in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_url_differs(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_main_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=False)

    r = validate_and_sync_repo("git@github.com:fakeorg/fakerepo.git", cfg.main_branch, target_path=target_path)
    assert r.has_errors()
    assert "requested url " in r.errors[0]
    assert "!= expected " in r.errors[0]


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_tag_equal(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_tag_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=False)

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.tag, target_path=target_path)
    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_tag_equal_depth_one(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_tag_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=True)

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.tag, target_path=target_path)
    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_commit_sha_equal(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_sha_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=False)

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.initial_commit_sha, target_path=target_path)
    assert not r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_sync_repo_commit_sha_equal_depth_one(
    tmp_path: Path, repo_runtime_config: RepoRuntimeConfig
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder

    _clone_sha_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one=True)

    r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.initial_commit_sha, target_path=target_path)
    assert not r.has_errors()


# @pytest.mark.slow
# @pytest.mark.git
# def test_validate_and_sync_repo_tag_different(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
#     cfg = RepoTestData()
#
#     target_path = tmp_path / cfg.destination_folder
#
#     _clone_dev_clean(target_path=target_path, repo_runtime_config=repo_runtime_config, depth_one = False)
#
#     repo = Repo(target_path)
#     # Delete local tag if it exists
#     assert cfg.tag in repo.tags
#     repo.delete_tag(cfg.tag)
#
#     # Create a lightweight tag
#     repo.create_tag(cfg.tag)
#     repo.git.checkout(cfg.tag)
#
#     r = validate_and_sync_repo(repo_runtime_config.repo_url, cfg.tag, target_path=target_path)
#     assert r.has_errors()
