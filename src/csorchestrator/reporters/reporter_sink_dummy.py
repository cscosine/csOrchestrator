from dataclasses import dataclass

from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase


@dataclass
class ReporterSinkDummy(ReporterSinkBase):
    def stdout(self, text: str) -> None:
        pass

    def stderr(self, text: str) -> None:
        pass

    def info(self, text: str) -> None:
        pass

    def warning(self, text: str) -> None:
        pass

    def error(self, text: str) -> None:
        pass
