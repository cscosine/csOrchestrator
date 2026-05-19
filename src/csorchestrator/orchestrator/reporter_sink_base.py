from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ReporterSinkBase(ABC):
    @abstractmethod
    def reset_indentation(self) -> None: ...

    @abstractmethod
    def increase_indentation(self) -> None: ...

    @abstractmethod
    def decrease_indentation(self) -> None: ...

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
