from dataclasses import dataclass

from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase


@dataclass
class ReporterSinkPrint(ReporterSinkBase):
    indentation: str = ""

    def reset_indentation(self) -> None:
        self.indentation = ""

    def increase_indentation(self) -> None:
        self.indentation += "  "

    def decrease_indentation(self) -> None:
        # slicing is safe
        self.indentation = self.indentation[:-2]

    def stdout(self, text: str) -> None:
        print(f"{self.indentation}[cout] {text}")

    def stderr(self, text: str) -> None:
        print(f"{self.indentation}[cerr] {text}")

    def info(self, text: str) -> None:
        print(f"{self.indentation}[info] {text}")

    def warning(self, text: str) -> None:
        print(f"{self.indentation}[warning] {text}")

    def error(self, text: str) -> None:
        print(f"{self.indentation}[error] {text}")
