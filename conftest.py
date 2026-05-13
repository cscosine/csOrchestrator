import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-all", action="store_true", default=False, help="Run all tests, including slow and git-dependent ones"
    )
    parser.addoption("--run-slow", action="store_true", default=False, help="Run tests marked as 'slow'")
    parser.addoption("--run-git", action="store_true", default=False, help="Run tests marked as 'git'")
    parser.addoption(
        "--requires-mandatory",
        action="store_true",
        default=False,
        help="Fail tests instead of skipping when required tools are missing",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    run_all = config.getoption("--run-all")
    run_slow = config.getoption("--run-slow")
    run_git = config.getoption("--run-git")

    # If run-all is enabled → do nothing (no skipping at all)
    if run_all:
        return

    if run_slow and run_git:
        return

    skip_slow = pytest.mark.skip(reason="need --run-slow or --run-all")
    skip_git = pytest.mark.skip(reason="need --run-git or --run-all")

    for item in items:
        if item.get_closest_marker("slow") and not run_slow:
            item.add_marker(skip_slow)

        if item.get_closest_marker("git") and not run_git:
            item.add_marker(skip_git)
