from csorchestrator.ci.github.github_workflow_config import (
    Cron,
    DayOfWeek,
    GitHubWorkflow,
    JobDescription,
    JobStrategy,
    MatrixOsArchCompilerGeneratorRunnerEntryInclude,
    create_github_wf,
    create_job_from_matrix,
)

EXPECTED_LINES_HEADER = [
    "name: test-wf-name",
    "",
    "on:",
    "  push:",
    "    branches:",
    "      - main",
    "      - dev",
    "    tags:",
    "      - 'v*.*.*'",
    "  pull_request:",
    "    branches:",
    "      - main",
    "  workflow_dispatch:",
    "  schedule:",
    "    - cron: '0 3 * * 1'",
    "",
]

EXPECTED_LINES = EXPECTED_LINES_HEADER + [
    "jobs:",
    "  the_job:",
    "    runs-on: ${{ matrix.runner }}",
    "",
    "    strategy:",
    "      fail-fast: false",
    "      matrix:",
    "        include:",
    "          - os: ubuntu22.04",
    "            arch: x64",
    "            compiler: gcc",
    "            generator: ninja",
    "            runner: ubuntu-22.04",
    "",
]


def test_workflow_with_triggers():
    wf = (
        GitHubWorkflow("test-wf-name")
        .on_push(branches=["main", "dev"], tags=["'v*.*.*'"])
        .on_pull_request(branches=["main"])
        .on_dispatch()
        .on_schedule(Cron.weekly(DayOfWeek.MON, hour=3))
    )

    assert wf.to_string_lines() == EXPECTED_LINES_HEADER


def test_workflow_with_triggers_and_one_job():
    wf = (
        GitHubWorkflow("test-wf-name")
        .on_push(branches=["main", "dev"], tags=["'v*.*.*'"])
        .on_pull_request(branches=["main"])
        .on_dispatch()
        .on_schedule(Cron.weekly(DayOfWeek.MON, hour=3))
        .on_job(
            job=JobDescription(
                name="the_job",
                runs_on=MatrixOsArchCompilerGeneratorRunnerEntryInclude.RUNS_ON_RUNNER_NAME,
                strategy=JobStrategy(fail_fast=False).on_matrix(
                    MatrixOsArchCompilerGeneratorRunnerEntryInclude(
                        os="ubuntu22.04",
                        arch="x64",
                        compiler="gcc",
                        generator="ninja",
                        runner="ubuntu-22.04",
                    )
                ),
            )
        )
    )

    assert wf.to_string_lines() == EXPECTED_LINES


def test_workflow_with_creation_helper():

    wf = create_github_wf(
        name="test-wf-name",
        on_push_branches=["main", "dev"],
        on_push_tags=["'v*.*.*'"],
        on_pull_request_branches=["main"],
        on_dispatch=True,
        on_schedule=Cron.weekly(DayOfWeek.MON, hour=3),
    ).on_job(
        job=create_job_from_matrix(
            name="the_job",
            matrix=MatrixOsArchCompilerGeneratorRunnerEntryInclude(
                os="ubuntu22.04",
                arch="x64",
                compiler="gcc",
                generator="ninja",
                runner="ubuntu-22.04",
            ),
        )
    )

    assert wf.to_string_lines() == EXPECTED_LINES
