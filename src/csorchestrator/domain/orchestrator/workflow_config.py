from abc import ABC
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TypeVar

# =========================================================
# Cron DSL
# =========================================================


class DayOfWeek(StrEnum):
    ANY = "*"
    MON = "1"
    TUE = "2"
    WED = "3"
    THU = "4"
    FRI = "5"
    SAT = "6"
    SUN = "0"


@dataclass(frozen=True, slots=True)
class Cron:
    minute: str = "0"
    hour: str = "0"
    day_of_month: str = "*"
    month: str = "*"
    day_of_week: DayOfWeek = DayOfWeek.ANY

    def to_string(self) -> str:
        return f"{self.minute} {self.hour} {self.day_of_month} {self.month} {self.day_of_week.value}"

    @staticmethod
    def daily(hour: int, minute: int = 0) -> "Cron":
        return Cron(str(minute), str(hour))

    @staticmethod
    def weekly(
        day: DayOfWeek,
        hour: int = 0,
        minute: int = 0,
    ) -> "Cron":
        return Cron(
            str(minute),
            str(hour),
            "*",
            "*",
            day,
        )

    @staticmethod
    def raw(expr: str) -> "Cron":
        parts = expr.split()

        if len(parts) != 5:
            raise ValueError("Cron expression must have exactly 5 fields")

        return RawCron(expr)


@dataclass(frozen=True, slots=True)
class RawCron(Cron):
    expr: str = ""

    def to_string(self) -> str:
        return self.expr


class ReleaseCreationOnTagConfigBaseCapability:
    pass


ReleaseCreationOnTagConfigBaseCapabilityT = TypeVar(
    "ReleaseCreationOnTagConfigBaseCapabilityT", bound=ReleaseCreationOnTagConfigBaseCapability
)


@dataclass
class ReleaseCreationOnTagConfigBase(ABC):
    name: str

    _capabilities: dict[type, ReleaseCreationOnTagConfigBaseCapability] = field(
        default_factory=dict,
        kw_only=True,
    )

    def add_capability(
        self,
        capability: ReleaseCreationOnTagConfigBaseCapability,
        key: type[ReleaseCreationOnTagConfigBaseCapability],  # use key = type(capability) to register as exact type,
        # but if need generic, use a specific subclass of ReleaseCreationOnTagConfigBaseCapability
    ) -> "ReleaseCreationOnTagConfigBase":
        self._capabilities[key] = capability
        return self

    def get_capability(
        self, t: type[ReleaseCreationOnTagConfigBaseCapabilityT]
    ) -> ReleaseCreationOnTagConfigBaseCapabilityT | None:
        capability = self._capabilities.get(t)
        return capability if isinstance(capability, t) else None

    def remove_capability(
        self,
        key: type[ReleaseCreationOnTagConfigBaseCapabilityT],
    ) -> "ReleaseCreationOnTagConfigBase":
        self._capabilities.pop(key, None)  # no exception if not exists
        return self


@dataclass
class WorkflowTrigger:
    on_push_branches: list[str] | None = None
    on_push_tags: list[str] | None = None
    on_pull_request_branches: list[str] | None = None
    on_dispatch: bool | None = None
    on_schedule: Cron | None = None


@dataclass
class WorkflowConfig:
    trigger: WorkflowTrigger
    create_release_on_tag: ReleaseCreationOnTagConfigBase | None = None
