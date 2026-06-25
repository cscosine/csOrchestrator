from dataclasses import dataclass, field
from typing import Self

from csorchestrator.ci.github.github_workflow_job_create_release import (
    JobReleaseCreationFromArifacts,
    job_release_on_tag_to_string_lines,
)
from csorchestrator.ci.github.github_workflow_triggers import (
    PullRequestTrigger,
    PushTrigger,
    ScheduleTrigger,
    TriggerType,
    TriggerUnion,
    WorkflowDispatchTrigger,
)
from csorchestrator.ci.github.guthub_workflow_matrix_constants import MatrixOsArchCompilerGeneratorGithubConstants
from csorchestrator.ci.github.utils import job_orchestrator_matrix_execution_to_string_lines
from csorchestrator.domain.orchestrator.step_base import (
    JobOrchestratorMatrixExecution,
    JobStrategy,
)
from csorchestrator.domain.orchestrator.workflow_config import Cron, MatrixOsArchCompilerGeneratorRunnerEntryInclude


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
