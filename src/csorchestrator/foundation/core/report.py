from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum


class ReportMessageType(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Report:
    """
    Collects error/warning/info messages.

    Attributes:
        errors: Critical issues that stop execution.
        warnings: Non-fatal issues that should be reviewed.
        infos: Informational messages for debugging and transparency.
    """

    _errors: list[str] = field(default_factory=list, init=False, repr=False)
    _warnings: list[str] = field(default_factory=list, init=False, repr=False)
    _infos: list[str] = field(default_factory=list, init=False, repr=False)
    _messages: list[tuple[ReportMessageType, str]] = field(default_factory=list, init=False)

    @property
    def errors(self) -> Sequence[str]:
        return tuple(self._errors)

    @property
    def warnings(self) -> Sequence[str]:
        return tuple(self._warnings)

    @property
    def infos(self) -> Sequence[str]:
        return tuple(self._infos)

    @property
    def messages(self) -> Sequence[tuple[ReportMessageType, str]]:
        return tuple(self._messages)

    def has_errors(self) -> bool:
        return len(self._errors) > 0

    def has_warnings(self) -> bool:
        return len(self._warnings) > 0

    def has_info(self) -> bool:
        return len(self._infos) > 0

    def append_error(self, msg: str) -> "Report":
        self._messages.append((ReportMessageType.ERROR, msg))
        self._errors.append(msg)
        return self

    def append_warning(self, msg: str) -> "Report":
        self._messages.append((ReportMessageType.WARNING, msg))
        self._warnings.append(msg)
        return self

    def append_info(self, msg: str) -> "Report":
        self._messages.append((ReportMessageType.INFO, msg))
        self._infos.append(msg)
        return self

    def append_report(self, other: "Report") -> None:
        """Merge another report into this one."""
        self._errors.extend(other.errors)
        self._warnings.extend(other.warnings)
        self._infos.extend(other.infos)
        self._messages.extend(other.messages)
