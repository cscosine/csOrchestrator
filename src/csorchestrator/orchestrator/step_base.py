from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar

from csorchestrator.ci.github.github_workflow_config import JobOrchestratorMatrixExecution
from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase


# base class for extra information that can be provided
class StepExtra:
    pass


T = TypeVar("T", bound="StepExtra")


# the step base class
@dataclass
class StepBase(ABC):
    name: str
    description: str
    _extras: dict[type, StepExtra] = field(
        default_factory=dict,
        kw_only=True,
    )

    def add_extra(
        self,
        extra: StepExtra,
    ) -> "StepBase":
        key = type(extra)
        self._extras[key] = extra
        return self

    def get_extra(self, t: type[T]) -> T | None:
        extra = self._extras.get(t)
        return extra if isinstance(extra, t) else None

    def remove_extra(
        self,
        key: type[T],
    ) -> "StepBase":
        self._extras.pop(key, None)  # no exception if not exists
        return self

    @classmethod
    @abstractmethod
    def createValidator(cls) -> "StepValidatorBase":
        raise NotImplementedError

    @abstractmethod
    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        raise NotImplementedError

    @abstractmethod
    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        raise NotImplementedError


@dataclass
class StepValidatorBase(ABC):
    @abstractmethod
    def validate(self, step: StepBase) -> Report:
        raise NotImplementedError


@dataclass
class StepValidatorNoOp(StepValidatorBase):
    def validate(self, step: StepBase) -> Report:
        return Report()
