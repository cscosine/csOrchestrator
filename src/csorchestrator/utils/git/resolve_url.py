import enum
import os

from csorchestrator.step.step_get_repository import RepoUrlParts


# return the token value if the token name is found in env, otherwise return None
def get_token_from_env(token_name: str) -> str | None:
    token = os.getenv(token_name)
    return token


# -------------------------
# ENUM
# -------------------------
class RepoUrlSelected(enum.StrEnum):
    HTTPS = "https"
    SSH = "ssh"


def select_https_or_ssh_url(
    https_url_template: RepoUrlParts, ssh_url: RepoUrlParts, token: str | None
) -> tuple[RepoUrlParts, RepoUrlSelected]:
    if token:
        return (
            RepoUrlParts(
                https_url_template.repo_base_url.format(token=token),
                https_url_template.repo_org,
                https_url_template.repo_name,
            )
        ), RepoUrlSelected.HTTPS
    else:
        return ssh_url, RepoUrlSelected.SSH


def select_https_or_ssh_url_resolve_token_name_on_env(
    https_url_template: RepoUrlParts, ssh_url: RepoUrlParts, token_name: str
) -> tuple[RepoUrlParts, RepoUrlSelected]:
    token = get_token_from_env(token_name)
    url, repo_url_selected = select_https_or_ssh_url(https_url_template, ssh_url, token)
    return url, repo_url_selected
