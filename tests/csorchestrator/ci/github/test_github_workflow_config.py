from csorchestrator.ci.github.github_workflow_config import (
    Cron,
    DayOfWeek,
    GitHubWorkflow,
    JobDescription,
    JobStrategy,
    MatrixOsArchCompilerGeneratorRunnerEntryInclude,
)


def test_workflow_with_triggers():
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
        "",
    ]


def test_workflow_with_triggers_and_one_job():
    wf = (
        GitHubWorkflow("test-wf-name")
        .on_push(branches=["main"])
        .on_pull_request(branches=["main"])
        .on_dispatch()
        .on_schedule(Cron.weekly(DayOfWeek.MON, hour=3))
        .on_job(
            job=JobDescription(
                name="the_job",
                strategy=JobStrategy(fail_fast=False).on_matrix_os_arch_compiler_generator_runner_entry_include(
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
        "",
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
