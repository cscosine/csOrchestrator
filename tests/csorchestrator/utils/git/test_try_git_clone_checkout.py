import logging
import os
from pathlib import Path

import pytest

from csorchestrator.utils.git.try_git_clone_checkout import try_git_clone_checkout

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# if the test is executed on github actions, we need a token to access it
# "ACTIONS_ORG_ACCESS" needs to be in the secrets of the csOrchestratorTestRepo
# and in the pytest job config as
#      - name: Run tests with coverage
#        env:
#          ACTIONS_ORG_ACCESS: ${{ secrets.ACTIONS_ORG_ACCESS }}
#        run: |
#          pytest [...]
token = os.getenv("ACTIONS_ORG_ACCESS")
if token:
    logger.info("test_try_git_clone_checkout using https access with ACTIONS_ORG_ACCESS token")
    repo_url = f"https://{token}@github.com/cscosine/csOrchestratorTestRepo.git"
else:
    logger.info("test_try_git_clone_checkout using ssh access")
    repo_url = "git@github.com:cscosine/csOrchestratorTestRepo.git"

## info for the test repo
repo_main_branch = "main"
repo_origin_main_branch = "origin/main"
repo_dev_branch = "dev"
repo_tag = "v1.0.0"
repo_non_existing_ref = "ref_does_not_exists"
repo_HEAD = "HEAD"
repo_initial_commit_sha = "63219a96b3d39cec4252791b49cfa215002487f2"
repo_refs_heads_main = "refs/heads/main"
repo_refs_remote_origin_main = "refs/remotes/origin/main"

destination_folder = "csOrchestratorTestRepo"

file_to_verify = "STATUS.txt"
expected_content_main = "tag"
expected_content_tag = "tag"
expected_content_dev = "dev"
expected_content_initial = "initial"


def _check_status(target_path: Path, expected_content: str) -> None:
    with open(target_path / "STATUS.txt", "r", encoding="utf-8") as f:
        first_line = f.readline().strip()

    assert first_line == expected_content


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_branch_main(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_main_branch, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()
    _check_status(target_path, expected_content_main)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_branch_main(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_main_branch, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()
    _check_status(target_path, expected_content_main)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_branch_dev(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_dev_branch, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()
    _check_status(target_path, expected_content_dev)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_branch_dev(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_dev_branch, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()
    _check_status(target_path, expected_content_dev)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_tag(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(repo_url=repo_url, repo_ref=repo_tag, target_path=target_path, depth_one=depth_one)

    assert not r.has_errors()
    _check_status(target_path, expected_content_tag)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_tag(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(repo_url=repo_url, repo_ref=repo_tag, target_path=target_path, depth_one=depth_one)

    assert not r.has_errors()
    _check_status(target_path, expected_content_tag)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_sha(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_initial_commit_sha, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()
    _check_status(target_path, expected_content_initial)


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_sha(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_initial_commit_sha, target_path=target_path, depth_one=depth_one
    )

    assert not r.has_errors()
    _check_status(target_path, expected_content_initial)


# not allowed cases
@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_non_existing_ref(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_non_existing_ref, target_path=target_path, depth_one=depth_one
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_non_existing_ref(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_non_existing_ref, target_path=target_path, depth_one=depth_one
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_branch_origin_main(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_origin_main_branch, target_path=target_path, depth_one=depth_one
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_branch_origin_main(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_origin_main_branch, target_path=target_path, depth_one=depth_one
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_HEAD(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(repo_url=repo_url, repo_ref=repo_HEAD, target_path=target_path, depth_one=depth_one)

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_HEAD(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(repo_url=repo_url, repo_ref=repo_HEAD, target_path=target_path, depth_one=depth_one)

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_refs_heads_main(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_refs_heads_main, target_path=target_path, depth_one=depth_one
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_refs_heads_main(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_refs_heads_main, target_path=target_path, depth_one=depth_one
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_full_depth_repo_refs_remote_origin_main(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = False

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_refs_remote_origin_main, target_path=target_path, depth_one=depth_one
    )

    assert r.has_errors()


@pytest.mark.slow
@pytest.mark.git
def test_simple_clone_depth_one_repo_refs_remote_origin_main(tmp_path) -> None:
    target_path = tmp_path / destination_folder
    depth_one = True

    assert not target_path.is_dir()

    r = try_git_clone_checkout(
        repo_url=repo_url, repo_ref=repo_refs_remote_origin_main, target_path=target_path, depth_one=depth_one
    )

    assert r.has_errors()
