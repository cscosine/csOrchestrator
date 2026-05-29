from dataclasses import dataclass, field
from enum import StrEnum
from typing import List, Optional, Self, TypeAlias

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
    runner: str

    RUNS_ON_RUNNER_NAME: str = "${{ matrix.runner }}"
    # deps: TODO add deps when we will need to install python packages

    def to_string_lines(self, indent: int = 0) -> list[str]:
        return [
            f"{_indent(indent)}include:",
            f"{_indent(indent + 2)}- os: {self.os}",
            f"{_indent(indent + 2)}  os_version: {self.os_version}",
            f"{_indent(indent + 2)}  architecture: {self.architecture}",
            f"{_indent(indent + 2)}  architecture_variant: {self.architecture_variant}",
            f"{_indent(indent + 2)}  compiler: {self.compiler}",
            f"{_indent(indent + 2)}  compiler_version: {self.compiler_version}",
            f"{_indent(indent + 2)}  generator: {self.build_generator}",
            f"{_indent(indent + 2)}  runner: {self.runner}",
        ]


MatrixEntryUnion: TypeAlias = MatrixOsArchCompilerGeneratorRunnerEntryInclude


@dataclass
class JobStrategy:
    fail_fast: bool
    _matrix_includes: list[MatrixEntryUnion] = field(default_factory=list)

    def to_string_lines(self, indent: int = 0) -> list[str]:
        fail_fast_str = "false"
        if self.fail_fast:
            fail_fast_str = "true"
        line_list = [
            f"{_indent(indent)}strategy:",
            f"{_indent(indent + 2)}fail-fast: {fail_fast_str}",
        ]
        if len(self._matrix_includes) > 0:
            line_list.append(f"{_indent(indent + 2)}matrix:")
            for matrix_include in self._matrix_includes:
                line_list += matrix_include.to_string_lines(indent + 4)
        return line_list

    def on_matrix(self, entry: MatrixOsArchCompilerGeneratorRunnerEntryInclude) -> "JobStrategy":
        self._matrix_includes.append(entry)
        return self


@dataclass
class JobDescription:
    name: str
    runs_on: str
    strategy: JobStrategy

    def to_string_lines(self, indent: int = 0) -> list[str]:
        line_list = [f"{_indent(indent)}{self.name}:", f"{_indent(indent + 2)}runs-on: {self.runs_on}", ""]
        line_list += self.strategy.to_string_lines(indent + 2)
        line_list += [""]
        return line_list


def create_job_from_matrix_list(
    name: str, matrix_list: list[MatrixOsArchCompilerGeneratorRunnerEntryInclude]
) -> JobDescription:

    jd = JobDescription(
        name=name,
        runs_on=MatrixOsArchCompilerGeneratorRunnerEntryInclude.RUNS_ON_RUNNER_NAME,
        strategy=JobStrategy(fail_fast=False),
    )

    for matrix in matrix_list:
        jd.strategy.on_matrix(matrix)

    return jd


@dataclass
class GitHubWorkflow:
    name: str
    _on: dict[str, TriggerUnion] = field(default_factory=dict)
    _jobs: list[JobDescription] = field(default_factory=list)

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
    def on_job(self, *, job: JobDescription) -> Self:
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
