import os

from csorchestrator.foundation.git.resolve_url import (
    RepoUrlParts,
    RepoUrlSelected,
    get_token_from_env,
    select_https_or_ssh_url,
    select_https_or_ssh_url_resolve_token_name_on_env,
)


def test_get_token_from_env_set():
    token_name = "TEST_TOKEN_ENV_VAR"
    token_value = "test_token_value"
    os.environ[token_name] = token_value
    assert get_token_from_env(token_name) == token_value
    del os.environ[token_name]


def test_get_token_from_env_not_set():
    token_name = "TEST_TOKEN_ENV_VAR_NOT_SET"
    if token_name in os.environ:
        del os.environ[token_name]
    assert get_token_from_env(token_name) is None


https_url_template = RepoUrlParts("https://{token}@github.com", "user", "repo.git")
ssh_url = RepoUrlParts("git@github.com:", "user", "repo.git")


def test_select_https_or_ssh_url_with_token():
    token = "test_token_value"
    url, sel = select_https_or_ssh_url(https_url_template, ssh_url, token)
    assert url == RepoUrlParts(
        https_url_template.repo_base_url.format(token=token), https_url_template.repo_org, https_url_template.repo_name
    )
    assert sel == RepoUrlSelected.HTTPS


def test_select_https_or_ssh_url_without_token():
    token = None
    url, sel = select_https_or_ssh_url(https_url_template, ssh_url, token)
    assert url == ssh_url
    assert sel == RepoUrlSelected.SSH


def test_select_https_or_ssh_url_resolve_token_name_on_env():
    token_name = "TEST_TOKEN_ENV_VAR"
    token_value = "test_token_value"
    os.environ[token_name] = token_value
    url, sel = select_https_or_ssh_url_resolve_token_name_on_env(https_url_template, ssh_url, token_name)
    assert url == RepoUrlParts(
        https_url_template.repo_base_url.format(token=token_value),
        https_url_template.repo_org,
        https_url_template.repo_name,
    )
    assert sel == RepoUrlSelected.HTTPS
    del os.environ[token_name]
