from dataclasses import dataclass, field
from typing import Self

from csorchestrator.domain.orchestrator.workflow_config import Cron
from csorchestrator.foundation.core.strings_utils import string_indent
from csorchestrator.frontend.github.github_workflow_job_create_release import (
    JobReleaseCreationFromArifacts,
    job_release_on_tag_to_string_lines,
)
from csorchestrator.frontend.github.github_workflow_matrix_constants import MatrixOsArchCompilerGeneratorGithubConstants
from csorchestrator.frontend.github.github_workflow_triggers import (
    PullRequestTrigger,
    PushTrigger,
    ScheduleTrigger,
    TriggerType,
    TriggerUnion,
    WorkflowDispatchTrigger,
)


# =========================================================
# Workflow builder
# =========================================================
@dataclass(frozen=True)
class MatrixOsArchCompilerGeneratorRunnerEntryInclude:
    execution_id: str
    os: str
    os_version: str
    architecture: str
    architecture_variant: str
    compiler: str
    compiler_version: str
    build_generator: str
    build_generator_type: str
    generator_cmake: str
    runner: str
    c_compiler: str | None = None
    cpp_compiler: str | None = None
    toolset: str | None = None


@dataclass
class JobStrategy:
    fail_fast: bool
    _matrix_includes: list[MatrixOsArchCompilerGeneratorRunnerEntryInclude] = field(default_factory=list)

    def add_matrix_include(self, entry: MatrixOsArchCompilerGeneratorRunnerEntryInclude) -> "JobStrategy":
        self._matrix_includes.append(entry)
        return self


class StepToStringLines:
    def to_string_lines(self, indent: int = 0) -> list[str]:
        raise NotImplementedError


@dataclass
class JobOrchestratorMatrixExecution:
    name: str
    runs_on: str
    strategy: JobStrategy
    steps: list[StepToStringLines] = field(default_factory=list)


def matrix_to_string_lines(mat: MatrixOsArchCompilerGeneratorRunnerEntryInclude, indent: int = 0) -> list[str]:
    list_str = [
        f"{string_indent(indent)}- execution_id: {mat.execution_id}",
        f"{string_indent(indent)}  os: {mat.os}",
        f"{string_indent(indent)}  os_version: {mat.os_version}",
        f"{string_indent(indent)}  architecture: {mat.architecture}",
        f"{string_indent(indent)}  architecture_variant: {mat.architecture_variant}",
        f"{string_indent(indent)}  compiler: {mat.compiler}",
    ]

    if mat.c_compiler is not None:
        list_str += [
            f"{string_indent(indent)}  c_compiler: {mat.c_compiler}",
        ]

    if mat.cpp_compiler is not None:
        list_str += [
            f"{string_indent(indent)}  cpp_compiler: {mat.cpp_compiler}",
        ]

    if mat.toolset is not None:
        list_str += [
            f"{string_indent(indent)}  toolset: {mat.toolset}",
        ]

    list_str += [
        f"{string_indent(indent)}  compiler_version: {mat.compiler_version}",
        f"{string_indent(indent)}  generator: {mat.build_generator}",
        f"{string_indent(indent)}  generator_type: {mat.build_generator_type}",
        f"{string_indent(indent)}  generator_cmake: {mat.generator_cmake}",
        f"{string_indent(indent)}  runner: {mat.runner}",
    ]
    return list_str


def job_strategy_to_string_lines(jobStrategy: JobStrategy, indent: int = 0) -> list[str]:
    fail_fast_str = str(jobStrategy.fail_fast).lower()
    line_list = [
        f"{string_indent(indent)}strategy:",
        f"{string_indent(indent + 2)}fail-fast: {fail_fast_str}",
    ]
    if len(jobStrategy._matrix_includes) > 0:
        line_list.append(f"{string_indent(indent + 2)}matrix:")
        line_list.append(f"{string_indent(indent + 4)}include:")
        for matrix_include in jobStrategy._matrix_includes:
            line_list += matrix_to_string_lines(matrix_include, indent + 6)
    return line_list


def job_orchestrator_matrix_execution_to_string_lines(
    jme: JobOrchestratorMatrixExecution, indent: int = 0
) -> list[str]:
    line_list = [f"{string_indent(indent)}{jme.name}:", f"{string_indent(indent + 2)}runs-on: {jme.runs_on}", ""]
    line_list += job_strategy_to_string_lines(jme.strategy, indent + 2)
    line_list += [""]
    if len(jme.steps) > 0:
        line_list += [f"{string_indent(indent + 2)}steps:"]
        for step in jme.steps:
            line_list += step.to_string_lines(indent + 4)
            line_list += [""]

    return line_list


def create_job_from_matrix_list(
    name: str,
    matrix_list: list[MatrixOsArchCompilerGeneratorRunnerEntryInclude],
    fail_fast: bool,
) -> JobOrchestratorMatrixExecution:

    jd = JobOrchestratorMatrixExecution(
        name=name,
        runs_on=MatrixOsArchCompilerGeneratorGithubConstants.MATRIX_RUNS_ON_RUNNER_NAME_EMBRACED,
        strategy=JobStrategy(fail_fast=fail_fast),
    )

    for matrix in matrix_list:
        jd.strategy.add_matrix_include(matrix)

    return jd


@dataclass
class GitHubWorkflow:
    name: str
    _on: dict[str, TriggerUnion] = field(default_factory=dict)
    _jobs_matrix_exec: list[JobOrchestratorMatrixExecution] = field(default_factory=list)
    _jobs_release_on_tag: list[JobReleaseCreationFromArifacts] = field(default_factory=list)

    # ---------------- PUSH ----------------

    def on_push(
        self,
        *,
        branches: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> Self:
        self._on[TriggerType.PUSH] = PushTrigger(branches, tags)
        return self

    # ---------------- PR ----------------

    def on_pull_request(
        self,
        *,
        branches: list[str] | None = None,
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
    def on_job_matrix_exec(self, job: JobOrchestratorMatrixExecution) -> Self:
        self._jobs_matrix_exec.append(job)
        return self

    def on_job_create_release_on_tag(self, job: JobReleaseCreationFromArifacts) -> Self:
        self._jobs_release_on_tag.append(job)
        return self

    # ---------------- OUTPUT ----------------

    def to_string_lines(self) -> list[str]:
        lines = [f"name: {self.name}"]
        lines += [""]
        lines += ["on:"]

        for trigger in self._on.values():
            lines.extend(trigger.to_string_lines(indent=2))
        lines += [""]

        if len(self._jobs_matrix_exec) > 0 or len(self._jobs_release_on_tag) > 0:
            lines += ["jobs:"]
            for job_r in self._jobs_release_on_tag:
                lines += job_release_on_tag_to_string_lines(job_r, indent=2)
            for job_m in self._jobs_matrix_exec:
                lines += job_orchestrator_matrix_execution_to_string_lines(job_m, indent=2)

        return lines
