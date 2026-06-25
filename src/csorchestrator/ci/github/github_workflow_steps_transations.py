from dataclasses import dataclass, field

from csorchestrator.domain.orchestrator.step_base import (
    StepToStringLines,
)
from csorchestrator.foundation.core.strings_utils import string_indent

# =========================================================
# Steps models
# =========================================================


@dataclass
class StepGitHubAction(StepToStringLines):
    name: str
    uses: str
    if_str: str | None = None
    with_list: list[str] = field(default_factory=list)

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{string_indent(indent)}- name: {self.name}"]
        lines += [f"{string_indent(indent)}  uses: {self.uses}"]
        if self.if_str is not None:
            lines += [f"{string_indent(indent)}  if: {self.if_str}"]
        if len(self.with_list) > 0:
            lines += [f"{string_indent(indent)}  with:"]
            for w in self.with_list:
                lines += [f"{string_indent(indent + 2)}  {w}"]
        return lines


@dataclass
class StepCheckoutRepositoryWith:
    repository: str | None
    path: str | None
    ref: str | None
    fetch_depth: str | None
    token: str | None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = []

        if self.repository:
            lines += [f"{string_indent(indent + 2)}repository: {self.repository}"]
        if self.path:
            lines += [f"{string_indent(indent + 2)}path: {self.path}"]
        if self.ref:
            lines += [f"{string_indent(indent + 2)}ref: {self.ref}"]
        if self.fetch_depth:
            lines += [f"{string_indent(indent + 2)}fetch-depth: {self.fetch_depth}"]
        if self.token:
            lines += [f"{string_indent(indent + 2)}token: {self.token}"]

        if len(lines) > 0:
            lines = [f"{string_indent(indent)}with:"] + lines

        return lines


@dataclass(frozen=True, slots=True)
class StepCheckoutRepository(StepToStringLines):
    name: str
    uses: str = "actions/checkout@v6"
    with_step: StepCheckoutRepositoryWith | None = None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{string_indent(indent)}- name: {self.name}"]
        lines += [f"{string_indent(indent)}  uses: {self.uses}"]
        if self.with_step is not None:
            lines += self.with_step.to_string_lines(indent + 2)

        return lines


@dataclass(frozen=True, slots=True)
class StepGitHubUploadArtifacts(StepToStringLines):
    name: str
    with_name: str
    with_path: str
    uses: str = "actions/upload-artifact@v7"

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{string_indent(indent)}- name: {self.name}"]
        lines += [f"{string_indent(indent)}  uses: {self.uses}"]
        lines += [f"{string_indent(indent)}  with:"]
        lines += [f"{string_indent(indent)}    name: {self.with_name}"]
        lines += [f"{string_indent(indent)}    path: {self.with_path}"]

        return lines


@dataclass(frozen=True, slots=True)
class StepRunCommand(StepToStringLines):
    name: str
    run: list[str]
    id: str | None = None
    if_str: str | None = None
    shell_type: str | None = None
    env: list[str] | None = None
    working_directory: str | None = None

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{string_indent(indent)}- name: {self.name}"]

        if self.id is not None:
            lines += [f"{string_indent(indent)}  id: {self.id}"]

        if self.if_str is not None:
            lines += [f"{string_indent(indent)}  if: {self.if_str}"]

        if self.env is not None and len(self.env) > 0:
            lines += [f"{string_indent(indent)}  env:"]
            for line in self.env:
                lines += [f"{string_indent(indent)}    {line}"]

        if self.shell_type is not None:
            lines += [f"{string_indent(indent)}  shell: {self.shell_type}"]

        if len(self.run) > 0:
            lines += [f"{string_indent(indent)}  run: {self.run[0]}"]
            for i in range(1, len(self.run)):
                lines += [f"{string_indent(indent)}    {self.run[i]}"]

        if self.working_directory is not None:
            lines += [f"{string_indent(indent)}  working-directory: {self.working_directory}"]

        return lines
