from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ReporterSinkBase(ABC):
    @abstractmethod
    def stdout(self, text: str) -> None: ...

    @abstractmethod
    def stderr(self, text: str) -> None: ...

    @abstractmethod
    def info(self, text: str) -> None: ...

    @abstractmethod
    def warning(self, text: str) -> None: ...

    @abstractmethod
    def error(self, text: str) -> None: ...
