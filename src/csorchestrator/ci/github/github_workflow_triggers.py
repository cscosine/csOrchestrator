from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from csorchestrator.orchestrator.workflow_config import Cron
from csorchestrator.utils.common.strings import string_indent

# =========================================================
# Trigger keys
# =========================================================


class TriggerType(StrEnum):
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    WORKFLOW_DISPATCH = "workflow_dispatch"
    SCHEDULE = "schedule"


# =========================================================
# Trigger models
# =========================================================


class Trigger:
    def to_string_lines(self, indent: int = 0) -> list[str]:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class PushTrigger(Trigger):
    branches: list[str] | None = None
    tags: list[str] | None = None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{string_indent(indent)}push:"]

        if self.branches is None and self.tags is None:
            return lines

        if self.branches is not None:
            lines.append(f"{string_indent(indent + 2)}branches:")

            for branch in self.branches:
                lines.append(f"{string_indent(indent + 4)}- {branch}")

        if self.tags is not None:
            lines.append(f"{string_indent(indent + 2)}tags:")

            for tag in self.tags:
                lines.append(f"{string_indent(indent + 4)}- {tag}")

        return lines


@dataclass(frozen=True, slots=True)
class PullRequestTrigger(Trigger):
    branches: list[str] | None = None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{string_indent(indent)}pull_request:"]

        if self.branches is None:
            return lines

        lines.append(f"{string_indent(indent + 2)}branches:")

        for branch in self.branches:
            lines.append(f"{string_indent(indent + 4)}- {branch}")

        return lines


@dataclass(frozen=True, slots=True)
class WorkflowDispatchTrigger(Trigger):
    def to_string_lines(self, indent: int = 0) -> list[str]:
        return [f"{string_indent(indent)}workflow_dispatch:"]


@dataclass(frozen=True, slots=True)
class ScheduleTrigger(Trigger):
    cron: Cron

    def to_string_lines(self, indent: int = 0) -> list[str]:
        return [
            f"{string_indent(indent)}schedule:",
            f"{string_indent(indent + 2)}- cron: '{self.cron.to_string()}'",
        ]


TriggerUnion: TypeAlias = PushTrigger | PullRequestTrigger | WorkflowDispatchTrigger | ScheduleTrigger
