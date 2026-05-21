from dataclasses import dataclass, field

from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase


@dataclass
class ReporterSinkMarkdown(ReporterSinkBase):
    lines: list[str] = field(default_factory=list)
    indentation: str = ""

    def increase_indentation(self) -> None:
        self.indentation += "  "

    def decrease_indentation(self) -> None:
        self.indentation = self.indentation[:-2]

    def stdout(self, text: str) -> None:
        self.lines.append(f"{self.indentation}  - {text}")

    def stderr(self, text: str) -> None:
        self.lines.append(f"{self.indentation}  - ❌ {text}")

    def info(self, text: str) -> None:
        self.lines.append(f"{self.indentation}  - ℹ️ {text}")

    def warning(self, text: str) -> None:
        self.lines.append(f"{self.indentation}  - ⚠️ {text}")

    def error(self, text: str) -> None:
        self.lines.append(f"{self.indentation}  - 🔥 {text}")
