from dataclasses import dataclass, field
from enum import StrEnum
from typing import List, Optional, Self, TypeAlias

from csorchestrator.context.orchestrator_minimal_description import OrchestratorExecutorMinimalDescription

# =========================================================
# Helpers
# =========================================================


def _indent(level: int) -> str:
    return " " * level


# =========================================================
# Trigger keys
# =========================================================


class TriggerType(StrEnum):
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    WORKFLOW_DISPATCH = "workflow_dispatch"
    SCHEDULE = "schedule"


# =========================================================
# Cron DSL
# =========================================================


class DayOfWeek(StrEnum):
    ANY = "*"
    MON = "1"
    TUE = "2"
    WED = "3"
    THU = "4"
    FRI = "5"
    SAT = "6"
    SUN = "0"


@dataclass(frozen=True, slots=True)
class Cron:
    minute: str = "0"
    hour: str = "0"
    day_of_month: str = "*"
    month: str = "*"
    day_of_week: DayOfWeek = DayOfWeek.ANY

    def to_string(self) -> str:
        return f"{self.minute} {self.hour} {self.day_of_month} {self.month} {self.day_of_week.value}"

    @staticmethod
    def daily(hour: int, minute: int = 0) -> "Cron":
        return Cron(str(minute), str(hour))

    @staticmethod
    def weekly(
        day: DayOfWeek,
        hour: int = 0,
        minute: int = 0,
    ) -> "Cron":
        return Cron(
            str(minute),
            str(hour),
            "*",
            "*",
            day,
        )

    @staticmethod
    def raw(expr: str) -> "Cron":
        parts = expr.split()

        if len(parts) != 5:
            raise ValueError("Cron expression must have exactly 5 fields")

        return RawCron(expr)


@dataclass(frozen=True, slots=True)
class RawCron(Cron):
    expr: str = ""

    def to_string(self) -> str:
        return self.expr


# =========================================================
# Trigger models
# =========================================================


class Trigger:
    def to_string_lines(self, indent: int = 0) -> list[str]:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class PushTrigger(Trigger):
    branches: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{_indent(indent)}push:"]

        if self.branches is None and self.tags is None:
            return lines

        if self.branches is not None:
            lines.append(f"{_indent(indent + 2)}branches:")

            for branch in self.branches:
                lines.append(f"{_indent(indent + 4)}- {branch}")

        if self.tags is not None:
            lines.append(f"{_indent(indent + 2)}tags:")

            for tag in self.tags:
                lines.append(f"{_indent(indent + 4)}- {tag}")

        return lines


@dataclass(frozen=True, slots=True)
class PullRequestTrigger(Trigger):
    branches: Optional[List[str]] = None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{_indent(indent)}pull_request:"]

        if self.branches is None:
            return lines

        lines.append(f"{_indent(indent + 2)}branches:")

        for branch in self.branches:
            lines.append(f"{_indent(indent + 4)}- {branch}")

        return lines


@dataclass(frozen=True, slots=True)
class WorkflowDispatchTrigger(Trigger):
    def to_string_lines(self, indent: int = 0) -> list[str]:
        return [f"{_indent(indent)}workflow_dispatch:"]


@dataclass(frozen=True, slots=True)
class ScheduleTrigger(Trigger):
    cron: Cron

    def to_string_lines(self, indent: int = 0) -> list[str]:
        return [
            f"{_indent(indent)}schedule:",
            f"{_indent(indent + 2)}- cron: '{self.cron.to_string()}'",
        ]


TriggerUnion: TypeAlias = PushTrigger | PullRequestTrigger | WorkflowDispatchTrigger | ScheduleTrigger


# =========================================================
# Workflow builder
# =========================================================
@dataclass(frozen=True)
class MatrixOsArchCompilerGeneratorRunnerEntryInclude:
    os: str
    os_version: str
    architecture: str
    architecture_variant: str
    compiler: str
    compiler_version: str
    build_generator: str
    build_generator_type: str
    runner: str
    # deps: TODO add deps when we will need to install python packages

    # embraced
    MATRIX_RUNS_ON_RUNNER_NAME_EMBRACED: str = "${{ matrix.runner }}"
    MATRIX_OS_NAME_EMBRACED: str = "${{ matrix.os }}"
    MATRIX_OS_VERSION_EMBRACED: str = "${{ matrix.os_version }}"
    MATRIX_ARCHITECTURE_EMBRACED: str = "${{ matrix.architecture }}"
    MATRIX_ARCHITECTURE_VARIANT_EMBRACED: str = "${{ matrix.architecture_variant }}"
    MATRIX_COMPILER_EMBRACED: str = "${{ matrix.compiler }}"
    MATRIX_COMPILER_VERSION_EMBRACED: str = "${{ matrix.compiler_version }}"
    MATRIX_GENERATOR_EMBRACED: str = "${{ matrix.generator }}"

    # not embraced
    MATRIX_GENERATOR_TYPE: str = "matrix.generator_type"

    def to_string_lines(self, indent: int = 0) -> list[str]:
        return [
            f"{_indent(indent)}- os: {self.os}",
            f"{_indent(indent)}  os_version: {self.os_version}",
            f"{_indent(indent)}  architecture: {self.architecture}",
            f"{_indent(indent)}  architecture_variant: {self.architecture_variant}",
            f"{_indent(indent)}  compiler: {self.compiler}",
            f"{_indent(indent)}  compiler_version: {self.compiler_version}",
            f"{_indent(indent)}  generator: {self.build_generator}",
            f"{_indent(indent)}  generator_type: {self.build_generator_type}",
            f"{_indent(indent)}  runner: {self.runner}",
        ]


@dataclass
class JobStrategy:
    fail_fast: bool
    _matrix_includes: list[MatrixOsArchCompilerGeneratorRunnerEntryInclude] = field(default_factory=list)

    def to_string_lines(self, indent: int = 0) -> list[str]:
        fail_fast_str = str(self.fail_fast).lower()
        line_list = [
            f"{_indent(indent)}strategy:",
            f"{_indent(indent + 2)}fail-fast: {fail_fast_str}",
        ]
        if len(self._matrix_includes) > 0:
            line_list.append(f"{_indent(indent + 2)}matrix:")
            line_list.append(f"{_indent(indent + 4)}include:")
            for matrix_include in self._matrix_includes:
                line_list += matrix_include.to_string_lines(indent + 6)
        return line_list

    def on_matrix(self, entry: MatrixOsArchCompilerGeneratorRunnerEntryInclude) -> "JobStrategy":
        self._matrix_includes.append(entry)
        return self


# =========================================================
# Steps models
# =========================================================


class Step:
    def to_string_lines(self, indent: int = 0) -> list[str]:
        raise NotImplementedError


@dataclass
class StepCheckoutRepositoryWith:
    repository: str | None
    path: str | None
    ref: str | None
    fetch_depth: str | None
    token: str | None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = []

        if self.repository:
            lines += [f"{_indent(indent + 2)}repository: {self.repository}"]
        if self.path:
            lines += [f"{_indent(indent + 2)}path: {self.path}"]
        if self.ref:
            lines += [f"{_indent(indent + 2)}ref: {self.ref}"]
        if self.fetch_depth:
            lines += [f"{_indent(indent + 2)}fetch-depth: {self.fetch_depth}"]
        if self.token:
            lines += [f"{_indent(indent + 2)}token: {self.token}"]

        if len(lines) > 0:
            lines = [f"{_indent(indent)}with:"] + lines

        return lines


@dataclass(frozen=True, slots=True)
class StepCheckoutRepository(Step):
    name: str
    uses: str = "actions/checkout@v6"
    with_step: StepCheckoutRepositoryWith | None = None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{_indent(indent)}- name: {self.name}"]
        lines += [f"{_indent(indent)}  uses: {self.uses}"]
        if self.with_step is not None:
            lines += self.with_step.to_string_lines(indent + 2)

        return lines


@dataclass(frozen=True, slots=True)
class StepGithubUploadArtifacts(Step):
    name: str
    with_name: str
    with_path: str
    uses: str = "actions/upload-artifact@v7"

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{_indent(indent)}- name: {self.name}"]
        lines += [f"{_indent(indent)}  uses: {self.uses}"]
        lines += [f"{_indent(indent)}  with:"]
        lines += [f"{_indent(indent)}    name: {self.with_name}"]
        lines += [f"{_indent(indent)}    path: {self.with_path}"]

        return lines


@dataclass(frozen=True, slots=True)
class StepRunCommand(Step):
    name: str
    run: list[str]
    id: str | None = None
    if_str: str | None = None
    shell_type: str | None = None
    env: list[str] | None = None
    working_directory: str | None = None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{_indent(indent)}- name: {self.name}"]

        if self.id is not None:
            lines += [f"{_indent(indent)}  id: {self.id}"]

        if self.if_str is not None:
            lines += [f"{_indent(indent)}  if: {self.if_str}"]

        if self.env is not None and len(self.env) > 0:
            lines += [f"{_indent(indent)}  env:"]
            for line in self.env:
                lines += [f"{_indent(indent)}    {line}"]

        if self.shell_type is not None:
            lines += [f"{_indent(indent)}  shell: {self.shell_type}"]

        if len(self.run) > 0:
            lines += [f"{_indent(indent)}  run: {self.run[0]}"]
            for i in range(1, len(self.run)):
                lines += [f"{_indent(indent)}    {self.run[i]}"]

        if self.working_directory is not None:
            lines += [f"{_indent(indent)}  working-directory: {self.working_directory}"]

        return lines


StepUnionType: TypeAlias = StepCheckoutRepository | StepRunCommand | StepGithubUploadArtifacts


@dataclass
class JobOrchestratorMatrixExecution:
    name: str
    runs_on: str
    orchestrator_desc: OrchestratorExecutorMinimalDescription
    strategy: JobStrategy
    steps: list[StepUnionType] = field(default_factory=list)

    def to_string_lines(self, indent: int = 0) -> list[str]:
        line_list = [f"{_indent(indent)}{self.name}:", f"{_indent(indent + 2)}runs-on: {self.runs_on}", ""]
        line_list += self.strategy.to_string_lines(indent + 2)
        line_list += [""]
        if len(self.steps) > 0:
            line_list += [f"{_indent(indent + 2)}steps:"]
            for step in self.steps:
                line_list += step.to_string_lines(indent + 4)
                line_list += [""]

        return line_list


@dataclass
class JobReleaseCreationFromArifacts:
    name: str
    needs: str
    runs_on: str
    if_str: str

    def to_string_lines(self, indent: int = 0) -> list[str]:
        line_list = [f"{_indent(indent)}{self.name}:"]
        line_list += [f"{_indent(indent + 2)}needs: {self.needs}"]
        line_list += [f"{_indent(indent + 2)}runs-on: {self.runs_on}"]
        line_list += [""]
        line_list += [f"{_indent(indent + 2)}if: {self.if_str}"]
        line_list += [""]
        line_list += [f"{_indent(indent + 2)}permissions:"]
        line_list += [f"{_indent(indent + 4)}contents: write"]
        line_list += [""]
        line_list += [f"{_indent(indent + 2)}steps:"]
        line_list += [f"{_indent(indent + 4)}- name: Download all artifacts"]
        line_list += [f"{_indent(indent + 6)}uses: actions/download-artifact@v8"]
        line_list += [f"{_indent(indent + 6)}with:"]
        line_list += [f"{_indent(indent + 8)}path: artifacts"]
        line_list += [""]
        line_list += [f"{_indent(indent + 4)}- name: Show downloaded files"]
        line_list += [f"{_indent(indent + 6)}run: find artifacts -type f"]
        line_list += [""]
        line_list += [f"{_indent(indent + 4)}- name: Create GitHub Release"]
        line_list += [f"{_indent(indent + 6)}uses: softprops/action-gh-release@v3"]
        line_list += [f"{_indent(indent + 6)}with:"]
        line_list += [f"{_indent(indent + 8)}files: |"]
        line_list += [f"{_indent(indent + 10)}artifacts/**/*    "]
        line_list += [""]
        return line_list


def create_job_from_matrix_list(
    name: str,
    matrix_list: list[MatrixOsArchCompilerGeneratorRunnerEntryInclude],
    orchestrator_desc: OrchestratorExecutorMinimalDescription,
    fail_fast: bool,
) -> JobOrchestratorMatrixExecution:

    jd = JobOrchestratorMatrixExecution(
        name=name,
        orchestrator_desc=orchestrator_desc,
        runs_on=MatrixOsArchCompilerGeneratorRunnerEntryInclude.MATRIX_RUNS_ON_RUNNER_NAME_EMBRACED,
        strategy=JobStrategy(fail_fast=fail_fast),
    )

    for matrix in matrix_list:
        jd.strategy.on_matrix(matrix)

    return jd


@dataclass
class GitHubWorkflow:
    name: str
    _on: dict[str, TriggerUnion] = field(default_factory=dict)
    _jobs: list[JobOrchestratorMatrixExecution | JobReleaseCreationFromArifacts] = field(default_factory=list)

    # ---------------- PUSH ----------------

    def on_push(
        self,
        *,
        branches: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
    ) -> Self:
        self._on[TriggerType.PUSH] = PushTrigger(branches, tags)
        return self

    # ---------------- PR ----------------

    def on_pull_request(
        self,
        *,
        branches: Optional[list[str]] = None,
    ) -> Self:
        self._on[TriggerType.PULL_REQUEST] = PullRequestTrigger(branches)
        return self

    # ---------------- DISPATCH ----------------

    def on_dispatch(self) -> Self:
        self._on[TriggerType.WORKFLOW_DISPATCH] = WorkflowDispatchTrigger()
        return self

    # ---------------- SCHEDULE ----------------

    def on_schedule(self, cron: Cron) -> Self:
        self._on[TriggerType.SCHEDULE] = ScheduleTrigger(cron)
        return self

    # ---------------- SCHEDULE ----------------
    def on_job(self, job: JobOrchestratorMatrixExecution) -> Self:
        self._jobs.append(job)
        return self

    # ---------------- OUTPUT ----------------

    def to_string_lines(self) -> list[str]:
        lines = [f"name: {self.name}"]
        lines += [""]
        lines += ["on:"]

        for trigger in self._on.values():
            lines.extend(trigger.to_string_lines(indent=2))
        lines += [""]

        if len(self._jobs) > 0:
            lines += ["jobs:"]
            for job in self._jobs:
                lines += job.to_string_lines(indent=2)

        return lines


@dataclass
class CreateGitHubWorkflowConfig:
    on_push_branches: list[str] | None = None
    on_push_tags: list[str] | None = None
    on_pull_request_branches: list[str] | None = None
    on_dispatch: bool | None = None
    on_schedule: Cron | None = None


def create_github_wf(name: str, *, config: CreateGitHubWorkflowConfig) -> GitHubWorkflow:

    gwf = GitHubWorkflow(name)
    if config.on_push_branches is not None or config.on_push_tags is not None:
        gwf.on_push(branches=config.on_push_branches, tags=config.on_push_tags)
    if config.on_pull_request_branches is not None:
        gwf.on_pull_request(branches=config.on_pull_request_branches)
    if config.on_dispatch:  # not None and true
        gwf.on_dispatch()
    if config.on_schedule is not None:
        gwf.on_schedule(config.on_schedule)
    return gwf
