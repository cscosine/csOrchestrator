import pytest

from csorchestrator.core.report import Report
from csorchestrator.reporters.orchestrator_executor_reporter_print import OrchestratorExecutorReporterPrint
from csorchestrator.reporters.reporter_sink_print import ReporterSinkPrint


def test_print_reporter_formats_reports_correctly(capsys: pytest.CaptureFixture[str]) -> None:
    reporter = OrchestratorExecutorReporterPrint(ReporterSinkPrint())

    # Test pre-execution report
    report = Report()
    report.append_error("Pre-check failed")
    report.append_warning("Low disk space")

    reporter.report_pre_execution_report(report)

    captured = capsys.readouterr()
    all_output = captured.out + captured.err
    assert "[error] Pre-check failed" in all_output
    assert "[warning] Low disk space" in all_output


def test_print_reporter_creation_report(capsys: pytest.CaptureFixture[str]) -> None:
    reporter = OrchestratorExecutorReporterPrint(ReporterSinkPrint())
    report = Report()
    report.append_info("Engine Ready")

    reporter.report_orchestrator_creation_report(report)
    captured = capsys.readouterr()
    all_output = captured.out + captured.err
    assert "[info] Engine Ready" in all_output
