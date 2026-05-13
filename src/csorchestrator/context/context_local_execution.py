# execution context
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from csorchestrator.context.context_os_architecture import ContextOsArchitecture, detect_context_os_architecture
from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.core.report import Report
from csorchestrator.utils.file_system.directory import ensure_directory_exists_or_create_and_is_usable


# create it with create_local_context to ensure is a valid path pointint to an existing (eventually created) folder
@dataclass(frozen=True)
class ContextLocalExecution:
    base_folder_path: Path
    os_architecture: ContextOsArchitecture


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
            ContextLocalExecution(base_folder_path=pr.result, os_architecture=osaExpected.value), report
        )
    else:
        return OptionalContextLocalExecutionWithReport.createReport(report)
