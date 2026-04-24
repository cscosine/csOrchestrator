import pytest

from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.core.report import Report


def test_optional_result_with_report():
    report = Report()
    report.errors.append("fail")
    report.warnings.append("be careful")
    report.infos.append("info")

    report_without_result = OptionalResultWithReport.createReport(report)
    assert not report_without_result.has_result()

    with pytest.raises(ValueError):
        report_without_result.result()

    assert report_without_result.result_or(33) == 33
    assert len(report_without_result.report.errors) == 1
    assert len(report_without_result.report.warnings) == 1
    assert len(report_without_result.report.infos) == 1

    optional_result_with_report = OptionalResultWithReport[int].createResultAndReport(42, report)
    assert optional_result_with_report.has_result()
    assert optional_result_with_report.result() == 42
    assert optional_result_with_report.result_or(33) == 42

    assert len(optional_result_with_report.report.errors) == 1
    assert len(optional_result_with_report.report.warnings) == 1
    assert len(optional_result_with_report.report.infos) == 1
