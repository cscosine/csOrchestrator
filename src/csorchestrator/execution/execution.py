from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeAlias

from csorchestrator.ci.github.github_workflow_config import (
    GitHubWorkflow,
    create_job_from_matrix_list,
)
from csorchestrator.ci.github.github_workflow_job_create_release import JobReleaseCreationFromArifacts
from csorchestrator.context.context_compiler_generator import (
    ContextCompilerGenerator,
    Generator,
    get_c_cpp_compiler,
    get_cmake_generator_name,
    get_cmake_toolset,
)
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
    ContextLocalExecutionExtra,
)
from csorchestrator.context.context_os_architecture import (
    OS,
    UBUNTU_STRING_PREFIX,
    UBUNTU_VERSIONS,
    WINDOWS_VERSIONS,
    Architecture,
    ContextOsArchitecture,
    detect_context_os_architecture,
)
from csorchestrator.context.context_os_architecture_compiler_generator import (
    ContextOsArchitectureCompilerGenerator,
    ExecutionMatrixOsArchCompilerGenerator,
    create_context_os_architecture_compiler_generator_string,
    create_context_os_architecture_string,
)
from csorchestrator.core.expected import Expected
from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.core.report import Report
from csorchestrator.execution.validated_orchestrator import create_validated_orchestrator
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.orchestrator_executor import (
    execute_orchestrator,
    executor_visit_reports_has_any_error,
)
from csorchestrator.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.orchestrator.orchestrator_minimal_description import OrchestratorExecutorMinimalDescription
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorExecutorVisitReports
from csorchestrator.orchestrator.workflow_config import MatrixOsArchCompilerGeneratorRunnerEntryInclude, WorkflowConfig
from csorchestrator.utils.file_system.directory import ensure_directory_exists_or_create_and_is_usable
from csorchestrator.visitors.orchestrator_visitor_github_wf_generator import (
    OrchestratorVisitorGitHubWorkflowPreparation,
)
from csorchestrator.visitors.orchestrator_visitor_local_executor import OrchestratorVisitorLocalExecutor


@dataclass
class ExecutionResult:
    # report of the validation phase, which is executed before the execution phase
    report_validation: OrchestratorExecutorVisitReports = field(default_factory=OrchestratorExecutorVisitReports)
    # report of the pre execution, before validation
    report_pre_execution: Report = field(default_factory=Report)
    # description of the execution, which is extracted from the orchestrator
    # before the execution phase
    execution_description: OrchestratorExecutorMinimalDescription | None = None

    # report of each execution phase (can be multiple if matrix is active), which is executed after the validation phase
    # if a matrix cycle is skipped (non executable locally, the list contains a None
    # if the matrix execution terminates before completing all the cycles (e.g. error in one of the cycle),
    #   the list contains only the executed cycles report, and then it is terminated
    #   (e.g. if 3 cycles, and error in the second, the list contains [report_cycle_1, report_cycle_2],
    #   and then it is terminated, without the report of the cycle 3)
    report_executions: list[OrchestratorExecutorVisitReports | None] = field(default_factory=list)

    def is_execution_successful(
        self,
    ) -> bool:
        if self.report_pre_execution.has_errors():
            return False

        for exec in self.report_executions:
            if exec is not None and executor_visit_reports_has_any_error(exec):
                return False
        return True


@dataclass
class OsArchitectureAndPath:
    os_architecture: ContextOsArchitecture
    path: Path


OptionalOsArchitectureAndPathWithReport: TypeAlias = OptionalResultWithReport[OsArchitectureAndPath]


def create_os_and_path(base_folder_path: str) -> OptionalOsArchitectureAndPathWithReport:
    report = Report()

    pr = ensure_directory_exists_or_create_and_is_usable(base_folder_path)

    report.append_report(pr.report)

    osaExpected = detect_context_os_architecture()

    if osaExpected.error is not None:
        report.append_error(osaExpected.error)

    if pr.result is not None and osaExpected.value is not None:
        return OptionalOsArchitectureAndPathWithReport.createResultAndReport(
            OsArchitectureAndPath(os_architecture=osaExpected.value, path=pr.result),
            report,
        )
    else:
        return OptionalOsArchitectureAndPathWithReport.createReport(report)


def validate_and_execute_orchestrator(
    orchestrator: Orchestrator, target_folder_path: str, reporter: OrchestratorExecutorReporterBase
) -> ExecutionResult:
    er = ExecutionResult()
    er.execution_description = orchestrator.extract_minimal_description()
    reporter.report_execution_description(er.execution_description)

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)
    er.report_pre_execution.append_report(orchestratorValidatedOpt.main_report)
    er.report_validation = orchestratorValidatedOpt.validation_reports
    reporter.report_validation_report(er.report_validation)

    if orchestratorValidatedOpt.orchestrator is None:
        reporter.report_pre_execution_report(er.report_pre_execution)
        reporter.finalize_execution()
        return er

    orchestrator = orchestratorValidatedOpt.orchestrator

    # validated orchestrator, create context

    os_and_path_opt = create_os_and_path(base_folder_path=target_folder_path)
    er.report_pre_execution.append_report(os_and_path_opt.report)

    if os_and_path_opt.result is None:
        reporter.report_pre_execution_report(er.report_pre_execution)
        reporter.finalize_execution()
        return er

    # finalized the pre execution
    reporter.report_pre_execution_report(er.report_pre_execution)

    os_and_path = os_and_path_opt.result

    matrix = orchestrator.execution_matrix

    matrix_extras: dict[type, ContextLocalExecutionExtra] = {}
    counter: int = 0
    for os_architecture_compiler_generator in matrix.os_architecture_compiler_generator_list:
        match = os_architecture_compiler_generator.context_os_architecture.can_be_executed_on(
            os_and_path.os_architecture
        )
        if not match:
            reporter.report_skip_execution(
                "skip orchestrator execution on not compatible matrix config: "
                f"{create_context_os_architecture_compiler_generator_string(os_architecture_compiler_generator)}"
                f", current os and architecture:  {create_context_os_architecture_string(os_and_path.os_architecture)}"
            )
            er.report_executions.append(None)
            continue
        # use the compatible os_arcchitecture, not the detected one.
        # e.g. detected os is win 11, but we select win 10 in the matrix, which is compatible

        context = ContextLocalExecution(
            base_folder_path=os_and_path.path,
            os_architecture=os_architecture_compiler_generator.context_os_architecture,
            active_compiler_generator=os_architecture_compiler_generator.context_compiler_generator,
            matrix_extras=matrix_extras,
            matrix_execution_id=str(counter),
        )

        # execute
        reporter.report_start_execution(
            "orchestrator execution on matrix config: "
            f"{create_context_os_architecture_compiler_generator_string(os_architecture_compiler_generator)}"
        )

        # execute the orchestrator visitor, which will execute the step to clone the repo, build, etc...
        report_execution = execute_orchestrator(
            orchestrator, OrchestratorVisitorLocalExecutor(context=context), reporter=reporter
        )

        if executor_visit_reports_has_any_error(report_execution):
            reporter.report_execution_report(report_execution)
            er.report_executions.append(report_execution)
            break

        reporter.report_execution_report(report_execution)

        er.report_executions.append(report_execution)

        matrix_extras = context.matrix_extras
        counter += 1

    reporter.finalize_execution()
    return er


OrchestratorMatrixToGitHubWFExpected: TypeAlias = Expected[
    list[MatrixOsArchCompilerGeneratorRunnerEntryInclude], list[str]
]  # str is the error messages

GITHUB_RUNNER_UBUNTU_22_04 = UBUNTU_STRING_PREFIX + "-22.04"
GITHUB_RUNNER_UBUNTU_24_04 = UBUNTU_STRING_PREFIX + "-24.04"
GITHUB_RUNNER_WINDOWS_2022 = OS.WINDOWS.value + "-2022"
GITHUB_RUNNER_WINDOWS_2025_VS2026 = OS.WINDOWS.value + "-2025-vs2026"


def get_runner(entry: ContextOsArchitectureCompilerGenerator) -> Expected[str, str]:
    os = entry.context_os_architecture.os
    os_version = entry.context_os_architecture.os_version
    arch = entry.context_os_architecture.architecture
    generator = entry.context_compiler_generator.build_generator.generator
    compiler_version = entry.context_compiler_generator.compiler_version

    if os == OS.LINUX:
        if os_version == UBUNTU_VERSIONS.UBUNTU_22_04.value:
            if arch == Architecture.X64:
                return Expected[str, str].make_value(GITHUB_RUNNER_UBUNTU_22_04)
        elif os_version == UBUNTU_VERSIONS.UBUNTU_24_04.value and arch == Architecture.X64:
            return Expected[str, str].make_value(GITHUB_RUNNER_UBUNTU_24_04)
    elif os == OS.WINDOWS and os_version == WINDOWS_VERSIONS.WIN10.value and arch == Architecture.X64:
        if generator == Generator.MSVC_17_2022:
            return Expected[str, str].make_value(GITHUB_RUNNER_WINDOWS_2022)
        elif generator == Generator.MSVC_18_2026:
            return Expected[str, str].make_value(GITHUB_RUNNER_WINDOWS_2025_VS2026)
        elif generator == Generator.NINJA or generator == Generator.NINJA_MULTI:
            if compiler_version == ContextCompilerGenerator.COMPILER_VERSION_MSVC_2026_18:
                return Expected[str, str].make_value(GITHUB_RUNNER_WINDOWS_2025_VS2026)
            elif compiler_version == ContextCompilerGenerator.COMPILER_VERSION_MSVC_2022_17:
                return Expected[str, str].make_value(GITHUB_RUNNER_WINDOWS_2022)

    return Expected[str, str].make_error(
        f"unsupported config os: {os.value}, os_version: {os_version}, arch: {arch.value}, generator: {generator.value}"
    )


def orchestrator_matrix_to_github_wf_matrix(
    orchestrator_matrix: ExecutionMatrixOsArchCompilerGenerator,
) -> OrchestratorMatrixToGitHubWFExpected:
    res: list[MatrixOsArchCompilerGeneratorRunnerEntryInclude] = []
    errors: list[str] = []

    counter: int = 0
    for entry in orchestrator_matrix.os_architecture_compiler_generator_list:
        runner_or_err = get_runner(entry)
        if runner_or_err.error is not None:
            errors.append(runner_or_err.error)
            continue

        assert runner_or_err.value is not None
        runner = runner_or_err.value

        generator_cmake = get_cmake_generator_name(entry.context_compiler_generator.build_generator.generator)
        if generator_cmake is None:
            errors.append(
                f"generator {entry.context_compiler_generator.build_generator.generator.value.lower()} does not have a "
                "CMake defined correspondent generator"
            )
            continue

        c_cpp_compiler = get_c_cpp_compiler(entry.context_compiler_generator.compiler_family)
        toolset = get_cmake_toolset(entry.context_compiler_generator.compiler_family)

        res.append(
            MatrixOsArchCompilerGeneratorRunnerEntryInclude(
                execution_id=str(counter),
                os=entry.context_os_architecture.os.value.lower(),
                os_version=entry.context_os_architecture.os_version.lower(),
                architecture=entry.context_os_architecture.architecture.value.lower(),
                architecture_variant=entry.context_os_architecture.architecture_variant.lower(),
                compiler=entry.context_compiler_generator.compiler_family.value.lower(),
                compiler_version=entry.context_compiler_generator.compiler_version.lower(),
                build_generator=entry.context_compiler_generator.build_generator.generator.value.lower(),
                build_generator_type=entry.context_compiler_generator.build_generator.generator_type.value.lower(),
                runner=runner,
                generator_cmake=generator_cmake,
                c_compiler=c_cpp_compiler[0],
                cpp_compiler=c_cpp_compiler[1],
                toolset=toolset,
            )
        )
        counter += 1
    if len(errors) > 0:
        return OrchestratorMatrixToGitHubWFExpected.make_error(errors)

    return OrchestratorMatrixToGitHubWFExpected.make_value(res)


def create_github_wf(name: str, *, config: WorkflowConfig) -> GitHubWorkflow:

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


def validate_and_generate_github_workflow(
    orchestrator: Orchestrator,
    script_folder_path: Path,
    output_path: Path | None,
    reporter: OrchestratorExecutorReporterBase,
) -> ExecutionResult:

    res = ExecutionResult()
    res.execution_description = orchestrator.extract_minimal_description()
    reporter.report_execution_description(res.execution_description)

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)
    res.report_pre_execution.append_report(orchestratorValidatedOpt.main_report)
    res.report_validation = orchestratorValidatedOpt.validation_reports
    reporter.report_validation_report(res.report_validation)

    if orchestratorValidatedOpt.orchestrator is None:
        reporter.report_pre_execution_report(res.report_pre_execution)
        reporter.finalize_execution()
        return res

    orchestrator = orchestratorValidatedOpt.orchestrator

    # validated orchestrator

    matrix = orchestrator.execution_matrix

    wf_matrix_or_errors = orchestrator_matrix_to_github_wf_matrix(matrix)
    if wf_matrix_or_errors.error is not None:
        for e in wf_matrix_or_errors.error:
            res.report_pre_execution.append_error(e)
        reporter.report_pre_execution_report(res.report_pre_execution)
        reporter.finalize_execution()
        return res

    assert wf_matrix_or_errors.value is not None
    wf_matrix = wf_matrix_or_errors.value

    if orchestrator.wf_config is None:
        res.report_pre_execution.append_error("github_workflow requires setting up the wf_config in orchestrator")
        reporter.report_pre_execution_report(res.report_pre_execution)
        reporter.finalize_execution()
        return res

    wf = create_github_wf(orchestrator.name, config=orchestrator.wf_config)

    if output_path is None:
        output_path = script_folder_path / Path(f".github/workflows/{wf.name}.yml")

    dir_creation_res = ensure_directory_exists_or_create_and_is_usable(str(output_path.parent.resolve()))
    res.report_pre_execution.append_report(dir_creation_res.report)

    if dir_creation_res.result is None:
        reporter.report_pre_execution_report(res.report_pre_execution)
        reporter.finalize_execution()
        return res

    # end pre execution
    reporter.report_pre_execution_report(res.report_pre_execution)

    if orchestrator.wf_config.create_release_on_tag is not None:
        wf.on_job_create_release_on_tag(
            JobReleaseCreationFromArifacts(
                name=orchestrator.wf_config.create_release_on_tag.name,
                needs=orchestrator.execution_matrix.name,
                runs_on="ubuntu-latest",
                if_str="${{ github.ref_type == 'tag' }}",
            )
        )

    wf_job = create_job_from_matrix_list(
        name=matrix.name,
        matrix_list=wf_matrix,
        fail_fast=matrix.fail_fast,
    )
    wf.on_job_matrix_exec(job=wf_job)

    reporter.report_start_execution("orchestrator execution without matrix")
    # execute the orchestrator visitor, which will execute the step to clone the repo, build, etc...
    report_execution = execute_orchestrator(
        orchestrator, OrchestratorVisitorGitHubWorkflowPreparation(wf_job), reporter=reporter
    )
    reporter.report_execution_report(report_execution)

    res.report_executions.append(report_execution)

    output_path.write_text("\n".join(wf.to_string_lines()), encoding="utf-8")
    return res
