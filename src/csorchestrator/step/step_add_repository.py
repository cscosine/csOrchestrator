from dataclasses import dataclass, field
from typing import Dict, Optional, Type, TypeVar

from csorchestrator.orchestrator.step_base import StepBase


# base class for extra information that can be provided
class StepAddRepositoryExtra:
    pass


@dataclass
class StepAddRepositoryExtraAccessToken(StepAddRepositoryExtra):
    token_name: str


T = TypeVar("T", bound="StepAddRepositoryExtra")


@dataclass
class StepAddRepository(StepBase):
    target_directory: str
    repo_url: str
    ref: str
    _extras: Dict[type, StepAddRepositoryExtra] = field(default_factory=dict)

    def add_extra(
        self,
        extra: StepAddRepositoryExtra,
    ) -> "StepAddRepository":
        key = type(extra)
        self._extras[key] = extra
        return self

    def get_extra(self, t: Type[T]) -> Optional[T]:
        extra = self._extras.get(t)
        return extra if isinstance(extra, t) else None
