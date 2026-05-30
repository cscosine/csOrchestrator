from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeAlias

from csorchestrator.ci.github.github_workflow_config import (
    MatrixOsArchCompilerGeneratorRunnerEntryInclude,
    create_job_from_matrix_list,
)
from csorchestrator.context.context_compiler_generator import Generator
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
    ContextLocalExecutionActiveMatrixConfig,
)
from csorchestrator.context.context_os_architecture import OS, Architecture, detect_context_os_architecture
from csorchestrator.context.context_os_architecture_compiler_generator import (
    ExecutionMatrixOsArchCompilerGenerator,
    MatrixSkipExecutionOnNonMatchingContext,
    create_context_os_architecture_compiler_generator_string,
)
from csorchestrator.core.expected import Expected
from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.orchestrator import Orchestrator, OrchestratorExecutorMinimalDescription
from csorchestrator.orchestrator.orchestrator_executor import (
    execute_orchestrator,
    flatten_orchestrator_executor_visit_reports,
)
from csorchestrator.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.orchestrator.orchestrator_visitor_base import OrchestratorExecutorVisitReports
from csorchestrator.orchestrator.validated_orchestrator import create_validated_orchestrator
from csorchestrator.utils.file_system.directory import ensure_directory_exists_or_create_and_is_usable
from csorchestrator.visitors.orchestrator_visitor_local_executor import OrchestratorVisitorLocalExecutor


@dataclass
class ExecutionResult:
    # report of the validation phase, which is executed before the execution phase
    report_pre_execution: Report = field(default_factory=Report)
    # description of the execution, which is extracted from the orchestrator
    # before the execution phase
    execution_description: OrchestratorExecutorMinimalDescription = field(
        default_factory=OrchestratorExecutorMinimalDescription
    )

    # report of each execution phase (can be multiple if matrix is active), which is executed after the validation phase
    # if a matrix cycle is skipped (non executable locally, the list contains a None
    report_executions: list[OrchestratorExecutorVisitReports | None] = field(default_factory=list)

    def is_execution_successful(
        self,
    ) -> bool:
        if self.report_pre_execution.has_errors():
            return False
        if self.report_executions is None:
            return False

        for exec in self.report_executions:
            if exec is not None:
                if flatten_orchestrator_executor_visit_reports(exec).has_errors():
                    return False
        return True


OptionalContextLocalExecutionWithReport: TypeAlias = OptionalResultWithReport[ContextLocalExecution]


def create_context_local_execution(base_folder_path: str) -> OptionalContextLocalExecutionWithReport:
    pr = ensure_directory_exists_or_create_and_is_usable(base_folder_path)

    report = Report()
    report.append_report(pr.report)

    osaExpected = detect_context_os_architecture()

    if osaExpected.error is not None:
        report.append_error(osaExpected.error)

    if pr.result is not None and osaExpected.value is not None:
        return OptionalContextLocalExecutionWithReport.createResultAndReport(
            ContextLocalExecution(base_folder_path=pr.result, os_architecture=osaExpected.value),
            report,
        )
    else:
        return OptionalContextLocalExecutionWithReport.createReport(report)


def validate_and_execute_orchestrator(
    orchestrator: Orchestrator, target_folder_path: str, reporter: OrchestratorExecutorReporterBase
) -> ExecutionResult:
    er = ExecutionResult()
    er.execution_description = orchestrator.extract_minimal_description()
    reporter.report_execution_description(er.execution_description)

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)
    er.report_pre_execution.append_report(orchestratorValidatedOpt.report)

    if orchestratorValidatedOpt.result is None:
        reporter.report_pre_execution_report(er.report_pre_execution)
        reporter.finalize_execution()
        return er

    reporter.report_pre_execution_report(er.report_pre_execution)

    orchestrator = orchestratorValidatedOpt.result

    # validated orchestrator, create context

    contextWithReport = create_context_local_execution(base_folder_path=target_folder_path)
    er.report_pre_execution.append_report(contextWithReport.report)

    if contextWithReport.result is None:
        reporter.report_pre_execution_report(er.report_pre_execution)
        reporter.finalize_execution()
        return er

    context = contextWithReport.result

    matrix = orchestrator.get_execution_matrix()
    if matrix is None:
        reporter.report_start_execution("orchestrator execution without matrix")
        # execute the orchestrator visitor, which will execute the step to clone the repo, build, etc...
        report_execution = execute_orchestrator(
            orchestrator, OrchestratorVisitorLocalExecutor(context=context), reporter=reporter
        )
        reporter.report_execution_report(report_execution)

        er.report_executions.append(report_execution)
    else:
        for os_architecture_compiler_generator in matrix.os_architecture_compiler_generator_list:
            excute_on_matching_context = matrix.get_extra(MatrixSkipExecutionOnNonMatchingContext)
            if excute_on_matching_context is not None:
                match = os_architecture_compiler_generator.context_os_architecture.is_equal_to(context.os_architecture)
                if not match:
                    reporter.report_skip_execution(
                        "skip orchestrator execution on not compatible matrix config: "
                        f"{create_context_os_architecture_compiler_generator_string(os_architecture_compiler_generator)}"
                    )
                    er.report_executions.append(None)
                    continue

            # execute
            reporter.report_start_execution(
                "orchestrator execution on matrix config: "
                f"{create_context_os_architecture_compiler_generator_string(os_architecture_compiler_generator)}"
            )

            context.add_extra(ContextLocalExecutionActiveMatrixConfig(os_architecture_compiler_generator))

            # execute the orchestrator visitor, which will execute the step to clone the repo, build, etc...
            report_execution = execute_orchestrator(
                orchestrator, OrchestratorVisitorLocalExecutor(context=context), reporter=reporter
            )

            context.remove_extra(ContextLocalExecutionActiveMatrixConfig)
            reporter.report_execution_report(report_execution)

            er.report_executions.append(report_execution)

    reporter.finalize_execution()
    return er


OrchestratorMatrixToGitHubWFExpected: TypeAlias = Expected[
    list[MatrixOsArchCompilerGeneratorRunnerEntryInclude], list[str]
]  # str is the error messages


def get_runner(os: OS, os_version: str, arch: Architecture, generator: Generator) -> Expected[str, str]:
    if os == OS.LINUX:
        if os_version == "ubuntu22.04":
            if arch == Architecture.X64:
                return Expected[str, str].make_value("ubuntu-22.04")
        elif os_version == "ubuntu24.04":
            if arch == Architecture.X64:
                return Expected[str, str].make_value("ubuntu-24.04")
    elif os == OS.WINDOWS:
        if os_version == "v10":
            if arch == Architecture.X64:
                if generator == Generator.MSVC_17_2022:
                    return Expected[str, str].make_value("windows-2022")
                elif generator == Generator.MSVC_18_2026:
                    return Expected[str, str].make_value("windows-2025-vs2026")

    return Expected[str, str].make_error(
        f"unsupported config os: {os.value}, os_version: {os_version}, arch: {arch.value}, generator: {generator.value}"
    )


def orchestrator_matrix_to_github_wf_matrix(
    orchestrator_matrix: ExecutionMatrixOsArchCompilerGenerator,
) -> OrchestratorMatrixToGitHubWFExpected:
    res: list[MatrixOsArchCompilerGeneratorRunnerEntryInclude] = []
    errors: list[str] = []

    for entry in orchestrator_matrix.os_architecture_compiler_generator_list:
        runner_or_err = get_runner(
            entry.context_os_architecture.os,
            entry.context_os_architecture.os_version,
            entry.context_os_architecture.architecture,
            entry.context_compiler_generator.build_generator.generator,
        )
        if runner_or_err.error is not None:
            errors.append(runner_or_err.error)
            continue

        assert runner_or_err.value is not None
        runner = runner_or_err.value

        res.append(
            MatrixOsArchCompilerGeneratorRunnerEntryInclude(
                os=entry.context_os_architecture.os.value.lower(),
                os_version=entry.context_os_architecture.os_version.lower(),
                architecture=entry.context_os_architecture.architecture.value.lower(),
                architecture_variant=entry.context_os_architecture.architecture_variant.lower(),
                compiler=entry.context_compiler_generator.compiler_family.value.lower(),
                compiler_version=entry.context_compiler_generator.compiler_version.lower(),
                build_generator=entry.context_compiler_generator.build_generator.generator.value.lower(),
                runner=runner,
            )
        )
    if len(errors) > 0:
        return OrchestratorMatrixToGitHubWFExpected.make_error(errors)

    return OrchestratorMatrixToGitHubWFExpected.make_value(res)


def validate_and_generate_github_workflow(
    orchestrator: Orchestrator,
    script_folder_path: Path,
    output_path: Path | None,
    reporter: OrchestratorExecutorReporterBase,
) -> ExecutionResult:

    res = ExecutionResult()

    orchestratorValidatedOpt = create_validated_orchestrator(orchestrator)
    res.report_pre_execution.append_report(orchestratorValidatedOpt.report)

    if orchestratorValidatedOpt.result is None:
        reporter.report_pre_execution_report(res.report_pre_execution)
        reporter.finalize_execution()
        return res

    orchestrator = orchestratorValidatedOpt.result

    # validated orchestrator

    matrix = orchestrator.get_execution_matrix()
    if matrix is None:
        res.report_pre_execution.append_error("github_workflow requires a execution matrix in the orchestrator")
        reporter.report_pre_execution_report(res.report_pre_execution)
        reporter.finalize_execution()
        return res

    wf_matrix_or_errors = orchestrator_matrix_to_github_wf_matrix(matrix)
    if wf_matrix_or_errors.error is not None:
        for e in wf_matrix_or_errors.error:
            res.report_pre_execution.append_error(e)
        reporter.report_pre_execution_report(res.report_pre_execution)
        reporter.finalize_execution()
        return res

    assert wf_matrix_or_errors.value is not None
    wf_matrix = wf_matrix_or_errors.value

    wf = orchestrator.default_github_wf  # TODO(wf) need a deep copy!
    if wf is None:
        res.report_pre_execution.append_error(
            "github_workflow requires setting up the default_github_wf in orchestrator"
        )
        reporter.report_pre_execution_report(res.report_pre_execution)
        reporter.finalize_execution()
        return res

    wf.on_job(
        job=create_job_from_matrix_list(
            name="the_job",
            matrix_list=wf_matrix,
        )
    )

    # TODO(wf) continue from here with executor and step additions

    if output_path is None:
        output_path = script_folder_path / Path(f".github/workflows/{wf.name}.yml")

    dir_creation_res = ensure_directory_exists_or_create_and_is_usable(str(output_path.parent.resolve()))
    res.report_pre_execution.append_report(dir_creation_res.report)

    if dir_creation_res.result is None:
        reporter.report_pre_execution_report(res.report_pre_execution)
        reporter.finalize_execution()
        return res

    output_path.write_text("\n".join(wf.to_string_lines()), encoding="utf-8")
    return res
