from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

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


@dataclass
class ReleaseCreationOnTagConfig:
    name: str
    publish_cs_orchestrator_manifest: bool
    base_install_dir: Path  # used only in local executions, not in github wf


@dataclass
class WorkflowConfig:
    on_push_branches: list[str] | None = None
    on_push_tags: list[str] | None = None
    on_pull_request_branches: list[str] | None = None
    on_dispatch: bool | None = None
    on_schedule: Cron | None = None
    create_release_on_tag: ReleaseCreationOnTagConfig | None = None
