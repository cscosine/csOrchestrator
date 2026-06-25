from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar

from csorchestrator.context.context_local_execution import ContextLocalExecution
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.workflow_config import MatrixOsArchCompilerGeneratorRunnerEntryInclude
from csorchestrator.foundation.core.report import Report


# base class for extra information that can be provided
class StepExtra:
    pass


StepExtraT = TypeVar("StepExtraT", bound="StepExtra")


@dataclass
class JobStrategy:
    fail_fast: bool
    _matrix_includes: list[MatrixOsArchCompilerGeneratorRunnerEntryInclude] = field(default_factory=list)

    def add_matrix_include(self, entry: MatrixOsArchCompilerGeneratorRunnerEntryInclude) -> "JobStrategy":
        self._matrix_includes.append(entry)
        return self


class StepToStringLines:
    def to_string_lines(self, indent: int = 0) -> list[str]:
        raise NotImplementedError


@dataclass
class JobOrchestratorMatrixExecution:
    name: str
    runs_on: str
    strategy: JobStrategy
    steps: list[StepToStringLines] = field(default_factory=list)


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

    def get_extra(self, t: type[StepExtraT]) -> StepExtraT | None:
        extra = self._extras.get(t)
        return extra if isinstance(extra, t) else None

    def remove_extra(
        self,
        key: type[StepExtraT],
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
