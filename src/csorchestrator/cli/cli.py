#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable, Literal, Optional, Sequence, cast

import click

from csorchestrator.core.expected import Expected
from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.core.report import Report
from csorchestrator.orchestrator.execution import validate_and_execute_orchestrator
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.orchestrator.orchestrator_executor_reporter_base import OrchestratorExecutorReporterBase
from csorchestrator.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.reporters.orchestrator_executor_reporter_composite import OrchestratorExecutorReporterComposite
from csorchestrator.reporters.orchestrator_executor_reporter_markdown import OrchestratorExecutorReporterMarkdown
from csorchestrator.reporters.orchestrator_executor_reporter_print import OrchestratorExecutorReporterPrint
from csorchestrator.reporters.reporter_sink_colorama_print import ReporterSinkColoramaPrint
from csorchestrator.reporters.reporter_sink_colored_print import ReporterSinkColoredPrint
from csorchestrator.reporters.reporter_sink_print import ReporterSinkPrint

CreateOrchestratorFn = Callable[[], OptionalResultWithReport[Orchestrator]]

SINK_TYPES = ("print", "colored", "colorama", "none")
SinkType = Literal["print", "colored", "colorama", "none"]  # keep aligned with SINK_TYPES


def _build_sink(kind: str) -> ReporterSinkBase | None:
    if kind == "print":
        return ReporterSinkPrint()
    elif kind == "colored":
        return ReporterSinkColoredPrint()
    elif kind == "colorama":
        return ReporterSinkColoramaPrint()
    elif kind == "none":
        return None
    else:
        r = ReporterSinkPrint()
        r.stderr(f"Unknown sink type: {kind}, fallback to ReporterSinkPrint")
        return r


@dataclass
class CLIConfig:
    sink: SinkType = "colorama"
    markdown_path: Optional[Path] = None


@click.group(help="csOrchestrator command line interface")  # type: ignore[untyped-decorator]
@click.option(  # type: ignore[untyped-decorator]
    "--sink",
    type=click.Choice(SINK_TYPES),
    default="colorama",
    show_default=True,
    help="Select reporter sink implementation",
)
@click.option(  # type: ignore[untyped-decorator]
    "--markdown",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write execution report as markdown file",
)
@click.pass_context  # type: ignore[untyped-decorator]
def app(ctx: click.Context, sink: str, markdown: Path | None = None) -> None:
    config = CLIConfig(sink=cast(SinkType, sink), markdown_path=markdown)
    ctx.ensure_object(dict)
    ctx.obj["config"] = config


def load_project_module(script_path: Path) -> Expected[ModuleType, str]:
    """Load a Python module from a file path."""
    script_path = script_path.resolve()
    module_name = f"csorchestrator_project_{script_path.stem}_{abs(hash(script_path))}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        return Expected[ModuleType, str].make_error(f"Unable to load project file '{script_path}'")

    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return Expected[ModuleType, str].make_value(module)


def resolve_target_folder(script_path: Path, target_folder: Path | None) -> Path:
    """Resolve the target folder, defaulting to script parent directory."""
    if target_folder is None:
        return script_path.parent.resolve()
    return target_folder.resolve()


def assert_create_orchestrator(module: ModuleType) -> Expected[CreateOrchestratorFn, str]:
    """Assert that the module defines create_orchestrator and return it."""
    if not hasattr(module, "create_orchestrator"):
        return Expected[CreateOrchestratorFn, str].make_error("Project script does not define create_orchestrator()")
    return Expected[CreateOrchestratorFn, str].make_value(module.create_orchestrator)


def execute_project_script(
    script_path: Path, target_folder: Path | None, reporter: OrchestratorExecutorReporterBase
) -> int:
    """Load and execute a project script's create_orchestrator() function."""

    module_or_error = load_project_module(script_path)
    if module_or_error.error is not None:
        report = Report()
        report.append_error(module_or_error.error)
        reporter.report_orchestrator_creation_report(report)
        return 1

    assert module_or_error.value is not None
    module = module_or_error.value

    create_orchestrator_expected = assert_create_orchestrator(module)
    if create_orchestrator_expected.error is not None:
        report = Report()
        report.append_error(create_orchestrator_expected.error)
        reporter.report_orchestrator_creation_report(report)
        return 1

    assert create_orchestrator_expected.value is not None
    create_orchestrator = create_orchestrator_expected.value

    orchestrator_result = create_orchestrator()

    reporter.report_orchestrator_creation_report(orchestrator_result.report)

    if orchestrator_result.result is None:
        return 1

    target_folder = resolve_target_folder(script_path, target_folder)
    validate_and_execute_orchestrator(orchestrator_result.result, str(target_folder), reporter)
    return 0


@app.command("run")  # type: ignore[untyped-decorator]
@click.argument(
    "script_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)  # type: ignore[untyped-decorator]
@click.option(
    "--target-folder",
    "-t",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Base folder for orchestrator execution. Defaults to the project script location.",
)  # type: ignore[untyped-decorator]
@click.pass_context  # type: ignore[untyped-decorator]
def run(ctx: click.Context, script_path: Path, target_folder: Path | None) -> int:
    """Load a Python project script and execute its create_orchestrator() result."""
    config: CLIConfig = ctx.obj["config"]

    reporter = OrchestratorExecutorReporterComposite()
    console_sink = _build_sink(config.sink)
    if console_sink is not None:
        reporter.reporters.append(OrchestratorExecutorReporterPrint(reporter_sink=console_sink))
    if config.markdown_path is not None:
        reporter.reporters.append(OrchestratorExecutorReporterMarkdown(path=config.markdown_path))

    return execute_project_script(script_path, target_folder, reporter)


def orchestrator_main_with_default_run(script_path: str, argv: Sequence[str] | None) -> int:
    """Invoke orchestrator CLI with default 'run' command if not specified."""
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        argv = ["run", script_path]
    elif argv[0] != "run":
        argv = ["run", script_path, *argv]
    return main(list(argv))


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    try:
        result = app.main(args=argv, standalone_mode=False)
    except SystemExit as exc:
        return int(exc.code or 0)

    if result is None:
        return 0
    return int(result)


if __name__ == "__main__":
    raise SystemExit(main())
