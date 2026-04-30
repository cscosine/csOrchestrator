import logging
from pathlib import Path

import pytest

from csorchestrator.utils.git.try_git_clone_checkout import try_git_clone_checkout
from tests.csorchestrator.utils.git.conftest import RepoRuntimeConfig
from tests.csorchestrator.utils.git.repo_config import RepoTestData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _check_status(target_path: Path, expected_content: str) -> None:
    cfg = RepoTestData()
    with open(target_path / cfg.file_to_verify, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()

    assert first_line == expected_content


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_branch_main(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url, repo_ref=cfg.main_branch, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()
    _check_status(target_path, cfg.expected_content_main)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_branch_main(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url, repo_ref=cfg.main_branch, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()
    _check_status(target_path, cfg.expected_content_main)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_branch_dev(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.dev_branch,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert not r.has_errors()
    _check_status(target_path, cfg.expected_content_dev)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_branch_dev(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.dev_branch,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert not r.has_errors()
    _check_status(target_path, cfg.expected_content_dev)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_tag(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url, repo_ref=cfg.tag, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()
    _check_status(target_path, cfg.expected_content_tag)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_tag(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url, repo_ref=cfg.tag, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()
    _check_status(target_path, cfg.expected_content_tag)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_sha(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.initial_commit_sha,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert not r.has_errors()
    _check_status(target_path, cfg.expected_content_initial)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_sha(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.initial_commit_sha,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert not r.has_errors()
    _check_status(target_path, cfg.expected_content_initial)


# not allowed cases
@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_non_existing_ref(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.non_existing_ref,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_non_existing_ref(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.non_existing_ref,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_branch_origin_main(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.origin_main_branch,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_branch_origin_main(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.origin_main_branch,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_HEAD(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url, repo_ref=cfg.head, target_path=target_path, depth_one=depth_one
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_HEAD(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url, repo_ref=cfg.head, target_path=target_path, depth_one=depth_one
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_refs_heads_main(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.refs_heads_main,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_refs_heads_main(tmp_path: Path, repo_runtime_config: RepoRuntimeConfig) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.refs_heads_main,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_repo_refs_remote_origin_main(
    tmp_path: Path, repo_runtime_config: RepoRuntimeConfig
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.refs_remote_origin_main,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_repo_refs_remote_origin_main(
    tmp_path: Path, repo_runtime_config: RepoRuntimeConfig
) -> None:
    cfg = RepoTestData()

    target_path = tmp_path / cfg.destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_runtime_config.repo_url,
        repo_ref=cfg.refs_remote_origin_main,
        target_path=target_path,
        depth_one=depth_one,
    )

    assert r.has_errors()
