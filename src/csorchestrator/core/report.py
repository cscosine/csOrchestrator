from dataclasses import dataclass, field
from typing import List


@dataclass
class Report:
    """
    Collects error/warning/info messages.

    Attributes:
        errors: Critical issues that stop execution.
        warnings: Non-fatal issues that should be reviewed.
        infos: Informational messages for debugging and transparency.
    """

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    infos: List[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def has_info(self) -> bool:
        return len(self.infos) > 0

    def append(self, other: "Report") -> None:
        """Merge another report into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.infos.extend(other.infos)

    # ANSI styling for terminal output
    _RED = "\033[31m"
    _YELLOW = "\033[33m"
    _BLUE = "\033[34m"
    _RESET = "\033[0m"
    _BOLD = "\033[1m"

    def print(self) -> None:
        """Pretty-print the report with colors."""
        if not (self.errors or self.warnings or self.infos):
            return

        print(f"{self._YELLOW}{self._BOLD}---------- REPORT ----------{self._RESET}")
        self._print_block("ERROR", self.errors, self._RED, bold=True)
        self._print_block("WARNING", self.warnings, self._YELLOW, bold=True)
        self._print_block("INFO", self.infos, self._BLUE)
        print(f"{self._YELLOW}{self._BOLD}----------------------------{self._RESET}")

    def _print_block(
        self,
        label: str,
        messages: List[str],
        color: str,
        bold: bool = False,
    ) -> None:
        """Print a block of messages under a category."""
        if not messages:
            return

        style = self._BOLD if bold else ""
        for msg in messages:
            print(f"{color}{style}[{label}]{self._RESET} {msg}")
