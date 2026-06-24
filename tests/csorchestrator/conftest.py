import logging

import pytest

from csorchestrator.utils.git.resolve_url import (
    RepoUrlParts,
    RepoUrlSelected,
    select_https_or_ssh_url_resolve_token_name_on_env,
)
from tests.csorchestrator.repo_test_data_config import RepoTestData

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def repo_url() -> RepoUrlParts:
    # return url
    repo_test_data = RepoTestData()
    repo_url, selected_url = select_https_or_ssh_url_resolve_token_name_on_env(
        https_url_template=repo_test_data.https_url_template,
        ssh_url=repo_test_data.ssh_url,
        token_name=repo_test_data.token_name,
    )
    match selected_url:
        case RepoUrlSelected.HTTPS:
            logger.info("using https access with token")
        case RepoUrlSelected.SSH:
            logger.info("using ssh access")
    return repo_url
