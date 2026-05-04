import os
from enum import Enum


# return the token value if the token name is found in env, otherwise return None
def get_token_from_env(token_name: str) -> str | None:
    token = os.getenv(token_name)
    return token


# -------------------------
# ENUM
# -------------------------
class RepoUrlSelected(str, Enum):
    HTTPS = "https"
    SSH = "ssh"


def select_https_or_ssh_url(https_url_template: str, ssh_url: str, token: str | None) -> tuple[str, RepoUrlSelected]:
    if token:
        return https_url_template.format(token=token), RepoUrlSelected.HTTPS
    else:
        return ssh_url, RepoUrlSelected.SSH


def select_https_or_ssh_url_resolve_token_name_on_env(
    https_url_template: str, ssh_url: str, token_name: str
) -> tuple[str, RepoUrlSelected]:
    token = get_token_from_env(token_name)
    url, repo_url_selected = select_https_or_ssh_url(https_url_template, ssh_url, token)
    return url, repo_url_selected
