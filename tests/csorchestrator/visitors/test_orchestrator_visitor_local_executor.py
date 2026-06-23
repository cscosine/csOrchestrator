from pathlib import Path

import pytest

from csorchestrator.cli.execution import create_os_and_path
from csorchestrator.cli.factory import create_orchestrator_factory_all_supported_cases
from csorchestrator.cli.validated_orchestrator import create_validated_orchestrator
from csorchestrator.context.context_compiler_generator import Compiler, ContextCompilerGenerator, GeneratorWithType
from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.orchestrator.orchestrator_executor import (
    execute_orchestrator,
    flatten_orchestrator_executor_visit_reports,
)
from csorchestrator.orchestrator.phase import Phase
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

    orchestrator = create_orchestrator_factory_all_supported_cases("myName", "0.0.0", "exec-job")
    orchestrator.add_phase(Phase(name="repos checkout").add_step(step))

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)

    assert orchestratorValidatedOpt.result is not None
    orchestrator = orchestratorValidatedOpt.result
    assert orchestrator is not None

    os_path_opt = create_os_and_path(str(tmp_path))
    assert os_path_opt.result is not None

    context = ContextLocalExecution(
        base_folder_path=os_path_opt.result.path,
        os_architecture=os_path_opt.result.os_architecture,
        active_compiler_generator=ContextCompilerGenerator(
            Compiler.GCC, ContextCompilerGenerator.COMPILER_VERSION_DEFAULT, GeneratorWithType.MSVC_17_2022
        ),
        matrix_execution_id="1",
    )

    ovb = OrchestratorVisitorLocalExecutor(context=context)

    # execute the orchestrator visitor, which will execute the step to clone the repo
    report = execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())
    flatten_report = flatten_orchestrator_executor_visit_reports(report)
    assert not flatten_report.has_errors()

    # execute the orchestrator visitor a second time, which will execute the step to update the repo,
    # which should succeed without errors
    report = execute_orchestrator(orchestrator, ovb, OrchestratorExecutorReporterDummy())
    flatten_report = flatten_orchestrator_executor_visit_reports(report)
    assert not flatten_report.has_errors()
