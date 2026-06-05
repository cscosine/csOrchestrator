from dataclasses import dataclass, field
from typing import TypeVar


# base class for extra information that can be provided
class StepExtra:
    pass


@dataclass
class StepExecuteOnlyOncePerMatrix(StepExtra):
    pass


T = TypeVar("T", bound="StepExtra")


# the step base class
@dataclass
class StepBase:
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
