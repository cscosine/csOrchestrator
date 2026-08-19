from dataclasses import dataclass
from enum import StrEnum
from typing import Any, TypeAlias

from csorchestrator.domain.orchestrator.workflow_config import Cron

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
    def to_dict(self) -> dict[str, object]:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class PushTrigger(Trigger):
    branches: list[str] | None = None
    tags: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}

        if self.branches is not None:
            d["branches"] = self.branches

        if self.tags is not None:
            d["tags"] = self.tags

        return {"push": d}


@dataclass(frozen=True, slots=True)
class PullRequestTrigger(Trigger):
    branches: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}

        if self.branches is not None:
            d["branches"] = self.branches

        return {"pull_request": d}


@dataclass(frozen=True, slots=True)
class WorkflowDispatchTrigger(Trigger):
    def to_dict(self) -> dict[str, Any]:
        return {"workflow_dispatch": {}}


@dataclass(frozen=True, slots=True)
class ScheduleTrigger(Trigger):
    cron: Cron

    def to_dict(self) -> dict[str, Any]:
        return {"schedule": [{"cron": self.cron.to_string()}]}


TriggerUnion: TypeAlias = PushTrigger | PullRequestTrigger | WorkflowDispatchTrigger | ScheduleTrigger
