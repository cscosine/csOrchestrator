from dataclasses import dataclass, field
from typing import Any

from csorchestrator.foundation.core.strings_utils import string_indent
from csorchestrator.frontend.github_workflow_translation.github_workflow_config import StepToStringLines
from csorchestrator.frontend.github_workflow_translation.YamlStringDumper import LiteralString

# =========================================================
# Steps models
# =========================================================


@dataclass
class StepGitHubAction(StepToStringLines):
    name: str
    uses: str
    id: str | None = None
    if_str: str | None = None
    with_list: list[str] = field(default_factory=list)

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{string_indent(indent)}- name: {self.name}"]
        if self.id is not None:
            lines += [f"{string_indent(indent)}  id: {self.id}"]
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
    with_path: list[str]
    uses: str = "actions/upload-artifact@v7"

    def to_string_lines(self, indent: int = 0) -> list[str]:
        lines = [f"{string_indent(indent)}- name: {self.name}"]
        lines += [f"{string_indent(indent)}  uses: {self.uses}"]
        lines += [f"{string_indent(indent)}  with:"]
        lines += [f"{string_indent(indent)}    name: {self.with_name}"]
        lines += [f"{string_indent(indent)}    path: |"]
        for p in self.with_path:
            lines += [f"{string_indent(indent)}      {p}"]
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

    def to_dict(self) -> dict[str, Any]:
        step_dict: dict[str, Any] = {
            "name": self.name,
            "run": LiteralString("\n".join(self.run)),
        }

        if self.id is not None:
            step_dict["id"] = self.id

        if self.if_str is not None:
            step_dict["if"] = self.if_str

        if self.shell_type is not None:
            step_dict["shell"] = self.shell_type

        if self.env is not None and len(self.env) > 0:
            env_dict: dict[str, str] = {}
            for line in self.env:
                key, value = line.split("=", 1)
                env_dict[key.strip()] = value.strip()
            step_dict["env"] = env_dict

        if self.working_directory is not None:
            step_dict["working-directory"] = self.working_directory

        return step_dict
