from dataclasses import dataclass, field

from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase


@dataclass
class ReporterSinkComposite(ReporterSinkBase):
    reporters: list[ReporterSinkBase] = field(default_factory=list)

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
