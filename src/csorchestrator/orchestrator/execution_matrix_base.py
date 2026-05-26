from abc import ABC, abstractmethod
from dataclasses import dataclass


# the orchestrator execution matrix base
@dataclass
class OrchestratorExecutionMatrixBase(ABC):
    @abstractmethod
    def to_list_string_description(self) -> list[str]:
        pass
