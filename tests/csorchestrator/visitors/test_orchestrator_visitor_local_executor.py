from dataclasses import dataclass
from pathlib import Path

import pytest

from csorchestrator.orchestrator.execution import create_context_local_execution
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.orchestrator_executor import (
    execute_orchestrator,
    flatten_orchestrator_executor_visit_reports,
)
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.step_base import StepBase
from csorchestrator.orchestrator.validated_orchestrator import create_validated_orchestrator
from csorchestrator.reporters.orchestrator_executor_reporter_dummy import OrchestratorExecutorReporterDummy
from csorchestrator.step.step_get_repository import (
    RepoUrlParts,
    StepGetRepositoryExtraDepthOne,
    StepGetRepositoryGitHub,
)
from csorchestrator.visitors.orchestrator_visitor_local_executor import OrchestratorVisitorLocalExecutor
from tests.csorchestrator.repo_test_data_config import RepoTestData


@pytest.mark.slow
@pytest.mark.git
def test_orchestrator_visitor_local_executor_succeed(tmp_path: Path, repo_url: RepoUrlParts) -> None:
    cfg = RepoTestData()

    step = StepGetRepositoryGitHub(
        name=cfg.repo_name,
        description=cfg.repo_name + " description",
        target_directory=cfg.destination_folder,
        repo_url_parts=repo_url,
        repo_ref=cfg.main_branch,
    ).add_extra(StepGetRepositoryExtraDepthOne(on_local_checkout=True, on_github_action_checkout=True))

    orchestrator = Orchestrator("myName")
    orchestrator.add_phase(Phase(name="repos checkout").add_step(step))

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)

    assert orchestratorValidatedOpt.result is not None
    orchestrator = orchestratorValidatedOpt.result
    assert orchestrator is not None

    context = create_context_local_execution(
        base_folder_path=str(tmp_path), orchestrator_desc=orchestrator.extract_minimal_description()
    )
    assert context.result is not None
    ovb = OrchestratorVisitorLocalExecutor(context=context.result)

    # execute the orchestrator visitor, which will execute the step to clone the repo
    report = execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())
    flatten_report = flatten_orchestrator_executor_visit_reports(report)
    assert not flatten_report.has_errors()

    # execute the orchestrator visitor a second time, which will execute the step to update the repo,
    # which should succeed without errors
    report = execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())
    flatten_report = flatten_orchestrator_executor_visit_reports(report)
    assert not flatten_report.has_errors()


@dataclass
class StepCustom1(StepBase):
    pass


def test_orchestrator_visitor_local_executor_fail_unknown_step(tmp_path: Path) -> None:

    orchestrator = Orchestrator("myName")
    orchestrator.add_phase(
        Phase(name="repos checkout").add_step(StepBase(name="unknown step", description="unknown step description"))
    )

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)

    assert orchestratorValidatedOpt.result is not None
    orchestrator = orchestratorValidatedOpt.result
    assert orchestrator is not None

    context = create_context_local_execution(
        base_folder_path=str(tmp_path), orchestrator_desc=orchestrator.extract_minimal_description()
    )
    assert context.result is not None
    ovb = OrchestratorVisitorLocalExecutor(context=context.result)

    # execute the orchestrator visitor, which will execute the step to clone the repo
    report = report = execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())
    flatten_report = flatten_orchestrator_executor_visit_reports(report)

    assert flatten_report.has_errors()
    assert "OrchestratorVisitorLocalExecutor cannot handle step" in flatten_report.errors[0]
