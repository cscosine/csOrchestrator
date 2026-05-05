from pathlib import Path

import pytest

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.orchestrator_executor import (
    OrchestratorExecutor,
    flatten_orchestrator_executor_visit_reports,
)
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.orchestrator.validated_orchestrator import create_validated_orchestrator
from csorchestrator.step.step_get_repository import RepositoryType, StepGetRepository, StepGetRepositoryExtraDepthOne
from csorchestrator.visitors.orchestrator_visitor_local_executor import OrchestratorVisitorLocalExecutor
from tests.csorchestrator.repo_test_data_config import RepoTestData


@pytest.mark.slow
@pytest.mark.git
def test_orchestrator_visitor_local_executor(tmp_path: Path, repo_url: str) -> None:
    cfg = RepoTestData()

    step = StepGetRepository(
        repo_type=RepositoryType.GIT,
        name=cfg.repo_name,
        description=cfg.repo_name + " description",
        target_directory=cfg.destination_folder,
        repo_url=repo_url,
        repo_ref=cfg.main_branch,
    ).add_extra(StepGetRepositoryExtraDepthOne(on_local_checkout=True, on_github_action_checkout=True))

    orchestrator = Orchestrator()
    orchestrator.add_phase(Phase(name="repos checkout").add_step(step))

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)

    assert orchestratorValidatedOpt.result is not None
    orchestrator = orchestratorValidatedOpt.result
    assert orchestrator is not None

    executor = OrchestratorExecutor(orchestrator)

    context = ContextLocalExecution(base_folder_path=tmp_path)
    ovb = OrchestratorVisitorLocalExecutor(context=context)

    # execute the orchestrator visitor, which will execute the step to clone the repo
    report = executor.execute(ovb)
    flatten_report = flatten_orchestrator_executor_visit_reports(report)
    flatten_report.print()
    assert not flatten_report.has_errors()

    # execute the orchestrator visitor a second time, which will execute the step to update the repo,
    # which should succeed without errors
    report = executor.execute(ovb)
    flatten_report = flatten_orchestrator_executor_visit_reports(report)
    flatten_report.print()
    assert not flatten_report.has_errors()
