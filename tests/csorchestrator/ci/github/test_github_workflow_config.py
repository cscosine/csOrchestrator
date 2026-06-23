from csorchestrator.ci.github.github_workflow_config import (
    GitHubWorkflow,
    create_job_from_matrix_list,
)
from csorchestrator.context.context_compiler_generator import (
    ContextCompilerGenerator,
    Generator,
    get_cmake_generator_name,
)
from csorchestrator.context.context_os_architecture import (
    ARCHITECTURE_VARIANT_GENERIC,
    OS,
    UBUNTU_VERSIONS,
    Architecture,
)
from csorchestrator.execution.execution import GITHUB_RUNNER_UBUNTU_22_04, create_github_wf
from csorchestrator.orchestrator.workflow_config import (
    Cron,
    DayOfWeek,
    MatrixOsArchCompilerGeneratorRunnerEntryInclude,
    WorkflowConfig,
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
    "          - execution_id: 1",
    "            os: linux",
    "            os_version: ubuntu22.04",
    f"            architecture: {Architecture.X64.value}",
    f"            architecture_variant: {ARCHITECTURE_VARIANT_GENERIC}",
    "            compiler: gcc",
    f"            compiler_version: {ContextCompilerGenerator.COMPILER_VERSION_DEFAULT}",
    "            generator: ninja",
    "            generator_type: single",
    "            generator_cmake: Ninja",
    f"            runner: {GITHUB_RUNNER_UBUNTU_22_04}",
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
        .on_job_matrix_exec(
            create_job_from_matrix_list(
                name="the_job",
                fail_fast=False,
                matrix_list=[
                    MatrixOsArchCompilerGeneratorRunnerEntryInclude(
                        execution_id="1",
                        os=OS.LINUX.value,
                        os_version=UBUNTU_VERSIONS.UBUNTU_22_04.value,
                        architecture=Architecture.X64.value,
                        architecture_variant=ARCHITECTURE_VARIANT_GENERIC,
                        compiler="gcc",
                        compiler_version=ContextCompilerGenerator.COMPILER_VERSION_DEFAULT,
                        build_generator="ninja",
                        build_generator_type="single",
                        runner=GITHUB_RUNNER_UBUNTU_22_04,
                        generator_cmake=get_cmake_generator_name(Generator.NINJA) or "",
                    )
                ],
            ),
        )
    )

    assert wf.to_string_lines() == EXPECTED_LINES


def test_workflow_with_creation_helper():

    wf = create_github_wf(
        name="test-wf-name",
        config=WorkflowConfig(
            on_push_branches=["main", "dev"],
            on_push_tags=["'v*.*.*'"],
            on_pull_request_branches=["main"],
            on_dispatch=True,
            on_schedule=Cron.weekly(DayOfWeek.MON, hour=3),
        ),
    ).on_job_matrix_exec(
        job=create_job_from_matrix_list(
            name="the_job",
            fail_fast=False,
            matrix_list=[
                MatrixOsArchCompilerGeneratorRunnerEntryInclude(
                    execution_id="1",
                    os=OS.LINUX.value,
                    os_version=UBUNTU_VERSIONS.UBUNTU_22_04.value,
                    architecture=Architecture.X64.value,
                    architecture_variant=ARCHITECTURE_VARIANT_GENERIC,
                    compiler="gcc",
                    compiler_version=ContextCompilerGenerator.COMPILER_VERSION_DEFAULT,
                    build_generator="ninja",
                    build_generator_type="single",
                    runner=GITHUB_RUNNER_UBUNTU_22_04,
                    generator_cmake=get_cmake_generator_name(Generator.NINJA) or "",
                )
            ],
        )
    )

    assert wf.to_string_lines() == EXPECTED_LINES
