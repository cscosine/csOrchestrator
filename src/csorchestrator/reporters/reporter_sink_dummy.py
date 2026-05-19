from dataclasses import dataclass

from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase


@dataclass
class ReporterSinkDummy(ReporterSinkBase):
    def reset_indentation(self) -> None:
        pass

    def increase_indentation(self) -> None:
        pass

    def decrease_indentation(self) -> None:
        pass

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
