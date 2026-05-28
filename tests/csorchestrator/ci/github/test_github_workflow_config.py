from csorchestrator.ci.github.github_workflow_config import (
    Cron,
    DayOfWeek,
    GitHubWorkflow,
)


def test_full_workflow():
    wf = (
        GitHubWorkflow("test-wf-name")
        .on_push(branches=["main"])
        .on_pull_request(branches=["main"])
        .on_dispatch()
        .on_schedule(Cron.weekly(DayOfWeek.MON, hour=3))
    )

    assert wf.to_string_lines() == [
        "name: test-wf-name",
        "",
        "on:",
        "  push:",
        "    branches:",
        "      - main",
        "  pull_request:",
        "    branches:",
        "      - main",
        "  workflow_dispatch:",
        "  schedule:",
        "    - cron: '0 3 * * 1'",
    ]
