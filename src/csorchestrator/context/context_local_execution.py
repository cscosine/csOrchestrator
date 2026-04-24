# execution context
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.utils.file_system.directory import ensure_directory_exists_or_create_and_is_usable


# create it with create_local_context to ensure is a valid path pointint to an existing (eventually created) folder
@dataclass(frozen=True)
class ContextLocalExecution:
    base_folder_path: Path


OptionalContextLocalExecutionWithReport: TypeAlias = OptionalResultWithReport[ContextLocalExecution]


def create_context_local_execution(path: str) -> OptionalContextLocalExecutionWithReport:
    pr = ensure_directory_exists_or_create_and_is_usable(path)

    if pr.result is not None:
        return OptionalContextLocalExecutionWithReport.createResultAndReport(
            ContextLocalExecution(base_folder_path=pr.result), pr.report
        )
    else:
        return OptionalContextLocalExecutionWithReport.createReport(pr.report)
