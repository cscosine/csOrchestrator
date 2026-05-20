from abc import ABC, abstractmethod
from dataclasses import dataclass

from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase


@dataclass
class ReporterSinkPrintBase(ReporterSinkBase, ABC):
    @abstractmethod
    def reset_indentation(self) -> None: ...

    @abstractmethod
    def increase_indentation(self) -> None: ...

    @abstractmethod
    def decrease_indentation(self) -> None: ...


@dataclass
class ReporterSinkPrint(ReporterSinkPrintBase):
    indentation: str = ""

    def reset_indentation(self) -> None:
        self.indentation = ""

    def increase_indentation(self) -> None:
        self.indentation += "  "

    def decrease_indentation(self) -> None:
        # slicing is safe
        self.indentation = self.indentation[:-2]

    def _print(self, prefix: str, text: str) -> None:
        prefix_str = f"{self.indentation}{prefix} "
        padding = " " * len(prefix_str)

        lines = text.splitlines() or [""]

        for i, line in enumerate(lines):
            if i == 0:
                print(f"{prefix_str}{line}")
            else:
                print(f"{padding}{line}")

    def stdout(self, text: str) -> None:
        self._print("[cout]", text)

    def stderr(self, text: str) -> None:
        self._print("[cerr]", text)

    def info(self, text: str) -> None:
        self._print("[info]", text)

    def warning(self, text: str) -> None:
        self._print("[warning]", text)

    def error(self, text: str) -> None:
        self._print("[error]", text)
