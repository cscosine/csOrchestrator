from pathlib import Path

import pytest

from csorchestrator.orchestrator.execution import ExecutionResult, validate_and_execute_orchestrator
from csorchestrator.orchestrator.orchestrator import Orchestrator, PhaseNameWithStepNames
from csorchestrator.orchestrator.phase import Phase
from csorchestrator.reporters.orchestrator_executor_reporter_dummy import OrchestratorExecutorReporterDummy
from csorchestrator.step.step_get_repository import RepositoryType, StepGetRepository, StepGetRepositoryExtraDepthOne
from tests.csorchestrator.repo_test_data_config import RepoTestData


@pytest.mark.slow
@pytest.mark.git
def test_validate_and_execute_orchestrator_success(tmp_path: Path, repo_url: str) -> None:
    cfg = RepoTestData()

    orchestrator = Orchestrator()

    step = StepGetRepository(
        repo_type=RepositoryType.GIT,
        name=cfg.repo_name,
        description=cfg.repo_name + " description",
        target_directory=cfg.destination_folder,
        repo_url=repo_url,
        repo_ref=cfg.main_branch,
    ).add_extra(StepGetRepositoryExtraDepthOne(on_local_checkout=True, on_github_action_checkout=True))

    orchestrator.add_phase(Phase(name="repos checkout").add_step(step))

    er: ExecutionResult = validate_and_execute_orchestrator(
        orchestrator, target_folder_path=str(tmp_path), reporter=OrchestratorExecutorReporterDummy()
    )
    assert not er.report_pre_execution.has_errors()
    assert er.execution_description.phases_and_steps == [
        PhaseNameWithStepNames(phase_name="repos checkout", step_names=[cfg.repo_name])
    ]
    assert len(er.report_execution) == len(er.execution_description.phases_and_steps)
    for phase_report in er.report_execution:
        for step_report in phase_report:
            assert not step_report.has_errors()


def test_validate_and_execute_orchestrator_fail_pre_execution(tmp_path: Path, repo_url: str) -> None:

    # create a file in the target folder path,
    # which cause the pre-execution validation to fail, since it expects a folder
    file_path = tmp_path / "file.txt"
    file_path.write_text("data")

    orchestrator = Orchestrator()

    er: ExecutionResult = validate_and_execute_orchestrator(
        orchestrator, target_folder_path=str(file_path), reporter=OrchestratorExecutorReporterDummy()
    )

    assert er.report_pre_execution.has_errors()


def test_validate_and_execute_orchestrator_fail_validation(tmp_path: Path, repo_url: str) -> None:
    cfg = RepoTestData()

    orchestrator = Orchestrator()

    step = StepGetRepository(
        repo_type=RepositoryType.GIT,
        name=cfg.repo_name,
        description=cfg.repo_name + " description",
        target_directory=cfg.destination_folder,
        repo_url=repo_url,
        repo_ref=cfg.main_branch,
    ).add_extra(StepGetRepositoryExtraDepthOne(on_local_checkout=True, on_github_action_checkout=True))

    p = Phase(name="repos checkout")
    # add the same step twice, which cause the validation to fail, since it expects unique step names per phase
    p.add_step(step)
    p.add_step(step)

    orchestrator.add_phase(p)

    er: ExecutionResult = validate_and_execute_orchestrator(
        orchestrator, target_folder_path=str(tmp_path), reporter=OrchestratorExecutorReporterDummy()
    )

    assert er.report_pre_execution.has_errors()
