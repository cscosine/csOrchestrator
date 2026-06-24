from shutil import which

import pytest


def has_tool(name: str) -> bool:
    return which(name) is not None


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    run_all = config.getoption("--run-all")
    if run_all:
        return  # 👈 CRITICAL: disable ALL requires logic

    requires_mandatory = config.getoption("--requires-mandatory")

    for item in items:
        marker = item.get_closest_marker("requires")
        if not marker:
            continue

        # supports multiple args: @requires("cl")
        tool = marker.args[0]

        if has_tool(tool):
            continue

        msg = f"Required tool missing: {tool}"

        if requires_mandatory:
            # tool not present → HARD FAIL
            raise pytest.UsageError(msg)
        else:
            # local mode → SKIP
            item.add_marker(pytest.mark.skip(reason=msg))
