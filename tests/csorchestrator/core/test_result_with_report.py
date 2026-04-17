import pytest
from csorchestrator.core.report import Report
from csorchestrator.core.result_with_report import ResultWithReport


def test_result_with_report():
    report = Report()
    report.errors.append("fail")
    report.warnings.append("be careful")
    report.infos.append("info")

    report_without_result = ResultWithReport.createReport(report)
    assert not report_without_result.has_result()

    with pytest.raises(ValueError):
        report_without_result.result()

    assert report_without_result.result_or(33) == 33
    assert len(report_without_result.report.errors) == 1
    assert len(report_without_result.report.warnings) == 1
    assert len(report_without_result.report.infos) == 1

    result_with_report = ResultWithReport[int].createResultAndReport(42, report)
    assert result_with_report.has_result()
    assert result_with_report.result() == 42
    assert result_with_report.result_or(33) == 42

    assert len(result_with_report.report.errors) == 1
    assert len(result_with_report.report.warnings) == 1
    assert len(result_with_report.report.infos) == 1
