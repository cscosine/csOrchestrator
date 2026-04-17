from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from csorchestrator.core.report import Report

T = TypeVar("T")


@dataclass
class ResultWithReport(Generic[T]):
    """
    Collects an optional generic result and a report
    """

    _result: Optional[T]
    report: Report

    def has_result(self) -> bool:
        return self._result is not None

    def result(self) -> T:
        if self._result is None:
            raise ValueError("No result present")
        return self._result

    def result_or(self, default: T) -> T:
        return self._result if self._result is not None else default

    @classmethod
    def createResultAndReport(cls, result: T, report: Report) -> "ResultWithReport[T]":
        return cls(result, report)

    @classmethod
    def createReport(cls, report: Report) -> "ResultWithReport[T]":
        return cls(None, report)
