import logging
import os
from dataclasses import dataclass

import pytest

from tests.csorchestrator.utils.git.repo_config import RepoTestData

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RepoRuntimeConfig:
    repo_url: str


@pytest.fixture(scope="session")
def repo_runtime_config() -> RepoRuntimeConfig:
    repo_test_data = RepoTestData()
    token = os.getenv(repo_test_data.token_name)

    if token:
        logger.info("using https access with token")
        return RepoRuntimeConfig(
            repo_url=repo_test_data.https_url_template.format(token=token),
        )
    else:
        logger.info("using ssh access")
        return RepoRuntimeConfig(
            repo_url=repo_test_data.ssh_url,
        )
