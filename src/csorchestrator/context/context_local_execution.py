# execution context
from dataclasses import dataclass
from pathlib import Path

from csorchestrator.context.context_os_architecture import ContextOsArchitecture


# create it with create_local_context to ensure is a valid path pointint to an existing (eventually created) folder
@dataclass(frozen=True)
class ContextLocalExecution:
    base_folder_path: Path
    os_architecture: ContextOsArchitecture
