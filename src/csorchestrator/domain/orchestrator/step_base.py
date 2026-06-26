from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar

from csorchestrator.foundation.core.report import Report


# base class for extra information that can be provided
class StepExtra:
    pass


StepExtraT = TypeVar("StepExtraT", bound=StepExtra)


class StepCapability:
    pass


StepCapabilityT = TypeVar("StepCapabilityT", bound=StepCapability)


# the step base class
@dataclass
class StepBase(ABC):
    name: str
    description: str

    _extras: dict[type, StepExtra] = field(
        default_factory=dict,
        kw_only=True,
    )

    _capabilities: dict[type, StepCapability] = field(
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

    def add_capability(
        self,
        capability: StepCapability,
        key: type[StepCapability],  # use key = type(capability) to register as exact type,
        # but if need generic, use a specific subclass of StepCapability
    ) -> "StepBase":
        self._capabilities[key] = capability
        return self

    def get_capability(self, t: type[StepCapabilityT]) -> StepCapabilityT | None:
        capability = self._capabilities.get(t)
        return capability if isinstance(capability, t) else None

    def remove_capability(
        self,
        key: type[StepCapabilityT],
    ) -> "StepBase":
        self._capabilities.pop(key, None)  # no exception if not exists
        return self


@dataclass
class StepValidatorBase(ABC):
    @abstractmethod
    def validate(self, step: StepBase) -> Report:
        raise NotImplementedError
