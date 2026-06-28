from csorchestrator.domain.context.context_compiler_generator import (
    ContextCompilerGenerator,
)
from csorchestrator.domain.context.context_os_architecture import (
    ARCHITECTURE_VARIANT_GENERIC,
    Architecture,
)
from csorchestrator.domain.orchestrator.workflow_config import (
    Cron,
    DayOfWeek,
)
from csorchestrator.frontend.github_workflow_translation.github_workflow_config import (
    GitHubWorkflow,
)
from csorchestrator.frontend.github_workflow_translation.validate_and_generate_github_workflow import (
    GITHUB_RUNNER_UBUNTU_22_04,
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
