from collections.abc import Sequence
from dataclasses import dataclass, field


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

    @property
    def errors(self) -> Sequence[str]:
        return tuple(self._errors)

    @property
    def warnings(self) -> Sequence[str]:
        return tuple(self._warnings)

    @property
    def infos(self) -> Sequence[str]:
        return tuple(self._infos)

    def has_errors(self) -> bool:
        return len(self._errors) > 0

    def has_warnings(self) -> bool:
        return len(self._warnings) > 0

    def has_info(self) -> bool:
        return len(self._infos) > 0

    def append_error(self, msg: str) -> "Report":
        self._errors.append(msg)
        return self

    def append_warning(self, msg: str) -> "Report":
        self._warnings.append(msg)
        return self

    def append_info(self, msg: str) -> "Report":
        self._infos.append(msg)
        return self

    def append_report(self, other: "Report") -> None:
        """Merge another report into this one."""
        self._errors.extend(other.errors)
        self._warnings.extend(other.warnings)
        self._infos.extend(other.infos)

    # ANSI styling for terminal output
    _RED = "\033[31m"
    _YELLOW = "\033[33m"
    _BLUE = "\033[34m"
    _RESET = "\033[0m"
    _BOLD = "\033[1m"

    def print(self) -> None:
        """Pretty-print the report with colors."""
        if not (self._errors or self._warnings or self._infos):
            return

        print(f"{self._YELLOW}{self._BOLD}---------- REPORT ----------{self._RESET}")
        self._print_block("ERROR", self._errors, self._RED, bold=True)
        self._print_block("WARNING", self._warnings, self._YELLOW, bold=True)
        self._print_block("INFO", self._infos, self._BLUE)
        print(f"{self._YELLOW}{self._BOLD}----------------------------{self._RESET}")

    def _print_block(
        self,
        label: str,
        messages: list[str],
        color: str,
        bold: bool = False,
    ) -> None:
        """Print a block of messages under a category."""
        if not messages:
            return

        style = self._BOLD if bold else ""
        for msg in messages:
            print(f"{color}{style}[{label}]{self._RESET} {msg}")
