from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Self

from csorchestrator.domain.context.context_os_architecture_compiler_generator import (
    ContextOsArchitectureCompilerGenerator,
)
from csorchestrator.domain.orchestrator.workflow_config import Cron
from csorchestrator.frontend.github_workflow_translation.github_workflow_job_create_release import (
    JobReleaseCreationFromArtifacts,
)
from csorchestrator.frontend.github_workflow_translation.github_workflow_matrix_constants import (
    MatrixOsArchCompilerGeneratorGithubConstants,
)
from csorchestrator.frontend.github_workflow_translation.github_workflow_triggers import (
    PullRequestTrigger,
    PushTrigger,
    ScheduleTrigger,
    Trigger,
    TriggerType,
    WorkflowDispatchTrigger,
)


# =========================================================
# Workflow builder
# =========================================================
@dataclass(frozen=True)
class MatrixOsArchCompilerGeneratorRunnerEntryInclude:
    original_os_architecture_compiler_generator_list: ContextOsArchitectureCompilerGenerator

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

    def to_dict(self) -> dict[str, Any]:
        ret = {
            "execution_id": self.execution_id,
            "os": self.os,
            "os_version": self.os_version,
            "architecture": self.architecture,
            "architecture_variant": self.architecture_variant,
            "compiler": self.compiler,
            "compiler_version": self.compiler_version,
            "generator": self.build_generator,
            "generator_type": self.build_generator_type,
            "generator_cmake": self.generator_cmake,
            "runner": self.runner,
        }
        if self.c_compiler is not None:
            ret["c_compiler"] = self.c_compiler

        if self.cpp_compiler is not None:
            ret["cpp_compiler"] = self.cpp_compiler

        if self.toolset is not None:
            ret["toolset"] = self.toolset

        return ret


@dataclass
class JobStrategy:
    fail_fast: bool
    _matrix_includes: list[MatrixOsArchCompilerGeneratorRunnerEntryInclude] = field(default_factory=list)

    def add_matrix_include(self, entry: MatrixOsArchCompilerGeneratorRunnerEntryInclude) -> "JobStrategy":
        self._matrix_includes.append(entry)
        return self

    def to_dict(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "fail-fast": self.fail_fast,
        }
        if len(self._matrix_includes) > 0:
            includes = []
            for matrix_include in self._matrix_includes:
                includes.append({"include": matrix_include.to_dict()})
            ret["matrix"] = includes

        return ret


class StepToDictInterface(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class JobOrchestratorMatrixExecution:
    name: str
    runs_on: str
    strategy: JobStrategy
    steps: list[StepToDictInterface] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            self.name: {
                "runs-on": self.runs_on,
                "strategy": self.strategy.to_dict(),
                "steps": [step.to_dict() for step in self.steps],
            }
        }


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
    _on: dict[str, Trigger] = field(default_factory=dict)
    _jobs_matrix_exec: list[JobOrchestratorMatrixExecution] = field(default_factory=list)
    _jobs_release_on_tag: list[JobReleaseCreationFromArtifacts] = field(default_factory=list)

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

    def on_job_create_release_on_tag(self, job: JobReleaseCreationFromArtifacts) -> Self:
        self._jobs_release_on_tag.append(job)
        return self

    # ---------------- OUTPUT ----------------

    def to_dict(self) -> dict[str, Any]:
        ret: dict[str, Any] = {}
        ret["name"] = self.name
        ret["on"] = [trigger.to_dict() for trigger in self._on.values()]
        if len(self._jobs_matrix_exec) > 0 or len(self._jobs_release_on_tag) > 0:
            release_jobs = [job.to_dict() for job in self._jobs_release_on_tag]
            matrix_jobs = [job.to_dict() for job in self._jobs_matrix_exec]
            jobs = release_jobs + matrix_jobs
            ret["jobs"] = jobs
        return ret
