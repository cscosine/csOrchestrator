from dataclasses import dataclass, field
from enum import StrEnum
from typing import List, Optional, Self, TypeAlias

# =========================================================
# Helpers
# =========================================================


def _indent(level: int) -> str:
    return " " * level


# =========================================================
# Trigger keys
# =========================================================


class TriggerType(StrEnum):
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    WORKFLOW_DISPATCH = "workflow_dispatch"
    SCHEDULE = "schedule"


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

    def render(self) -> str:
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

    def render(self) -> str:
        return self.expr


# =========================================================
# Trigger models
# =========================================================


class Trigger:
    def to_string_lines(self, indent: int = 0) -> list[str]:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class PushTrigger(Trigger):
    branches: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{_indent(indent)}push:"]

        if self.branches is None and self.tags is None:
            return lines

        if self.branches is not None:
            lines.append(f"{_indent(indent + 2)}branches:")

            for branch in self.branches:
                lines.append(f"{_indent(indent + 4)}- {branch}")

        if self.tags is not None:
            lines.append(f"{_indent(indent + 2)}tags:")

            for tag in self.tags:
                lines.append(f"{_indent(indent + 4)}- {tag}")

        return lines


@dataclass(frozen=True, slots=True)
class PullRequestTrigger(Trigger):
    branches: Optional[List[str]] = None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{_indent(indent)}pull_request:"]

        if self.branches is None:
            return lines

        lines.append(f"{_indent(indent + 2)}branches:")

        for branch in self.branches:
            lines.append(f"{_indent(indent + 4)}- {branch}")

        return lines


@dataclass(frozen=True, slots=True)
class WorkflowDispatchTrigger(Trigger):
    def to_string_lines(self, indent: int = 0) -> list[str]:
        return [f"{_indent(indent)}workflow_dispatch:"]


@dataclass(frozen=True, slots=True)
class ScheduleTrigger(Trigger):
    cron: Cron

    def to_string_lines(self, indent: int = 0) -> list[str]:
        return [
            f"{_indent(indent)}schedule:",
            f"{_indent(indent + 2)}- cron: '{self.cron.render()}'",
        ]


TriggerUnion: TypeAlias = PushTrigger | PullRequestTrigger | WorkflowDispatchTrigger | ScheduleTrigger


# =========================================================
# Workflow builder
# =========================================================


@dataclass
class GitHubWorkflow:
    name: str
    _on: dict[str, TriggerUnion] = field(default_factory=dict)

    # ---------------- PUSH ----------------

    def on_push(
        self,
        *,
        branches: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
    ) -> Self:
        self._on[TriggerType.PUSH] = PushTrigger(branches, tags)
        return self

    # ---------------- PR ----------------

    def on_pull_request(
        self,
        *,
        branches: Optional[list[str]] = None,
    ) -> Self:
        self._on[TriggerType.PULL_REQUEST] = PullRequestTrigger(branches)
        return self

    # ---------------- DISPATCH ----------------

    def on_dispatch(self) -> Self:
        self._on[TriggerType.WORKFLOW_DISPATCH] = WorkflowDispatchTrigger()
        return self

    # ---------------- SCHEDULE ----------------

    def on_schedule(self, cron: Cron) -> Self:
        self._on[TriggerType.SCHEDULE] = ScheduleTrigger(cron)
        return self

    # ---------------- OUTPUT ----------------

    def to_string_lines(self) -> list[str]:
        lines = [f"name: {self.name}"]
        lines += [""]
        lines += ["on:"]

        for trigger in self._on.values():
            lines.extend(trigger.to_string_lines(indent=2))

        return lines

    def render(self) -> str:
        return "\n".join(self.to_string_lines())
