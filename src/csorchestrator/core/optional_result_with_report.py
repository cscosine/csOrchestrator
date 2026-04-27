from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from csorchestrator.core.report import Report

T = TypeVar("T")


@dataclass
class OptionalResultWithReport(Generic[T]):
    """
    Collects an optional generic result and a report
    """

    report: Report
    result: Optional[T] = None

    def has_result(self) -> bool:
        return self.result is not None

    def result_or(self, default: T) -> T:
        return self.result if self.result is not None else default

    @classmethod
    def createResultAndReport(cls, result: T, report: Report) -> "OptionalResultWithReport[T]":
        return cls(report, result)

    @classmethod
    def createReport(cls, report: Report) -> "OptionalResultWithReport[T]":
        return cls(report)
