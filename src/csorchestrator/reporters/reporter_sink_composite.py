from dataclasses import dataclass, field

from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase


@dataclass
class ReporterSinkComposite(ReporterSinkBase):
    reporters: list[ReporterSinkBase] = field(default_factory=list)

    def reset_indentation(self) -> None:
        for r in self.reporters:
            r.reset_indentation()

    def increase_indentation(self) -> None:
        for r in self.reporters:
            r.increase_indentation()

    def decrease_indentation(self) -> None:
        for r in self.reporters:
            r.decrease_indentation()

    def stdout(self, text: str) -> None:
        for r in self.reporters:
            r.stdout(text)

    def stderr(self, text: str) -> None:
        for r in self.reporters:
            r.stderr(text)

    def info(self, text: str) -> None:
        for r in self.reporters:
            r.info(text)

    def warning(self, text: str) -> None:
        for r in self.reporters:
            r.warning(text)

    def error(self, text: str) -> None:
        for r in self.reporters:
            r.error(text)
