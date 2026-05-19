from csorchestrator.core.report import Report, ReportMessageType


def test_report_append_and_print(capfd):
    r1 = Report()
    r1.append_error("fail")
    assert len(r1.errors) == 1
    assert r1.has_errors()
    assert len(r1.warnings) == 0
    assert not r1.has_warnings()
    assert len(r1.infos) == 0
    assert not r1.has_info()
    assert len(r1.messages) == 1
    assert r1.messages[0] == (ReportMessageType.ERROR, "fail")

    r1.append_warning("be careful")
    assert len(r1.errors) == 1
    assert r1.has_errors()
    assert len(r1.warnings) == 1
    assert r1.has_warnings()
    assert len(r1.infos) == 0
    assert not r1.has_info()
    assert len(r1.messages) == 2
    assert r1.messages[0] == (ReportMessageType.ERROR, "fail")
    assert r1.messages[1] == (ReportMessageType.WARNING, "be careful")

    r1.append_info("info")
    assert len(r1.errors) == 1
    assert r1.has_errors()
    assert len(r1.warnings) == 1
    assert r1.has_warnings()
    assert len(r1.infos) == 1
    assert r1.has_info()
    assert len(r1.messages) == 3
    assert r1.messages[0] == (ReportMessageType.ERROR, "fail")
    assert r1.messages[1] == (ReportMessageType.WARNING, "be careful")
    assert r1.messages[2] == (ReportMessageType.INFO, "info")

    r2 = Report()
    r2.append_error("another")
    assert len(r2.errors) == 1
    assert len(r2.warnings) == 0
    assert len(r2.infos) == 0
    assert len(r2.messages) == 1
    assert r2.messages[0] == (ReportMessageType.ERROR, "another")

    # merge reports
    r1.append_report(r2)
    assert len(r1.errors) == 2
    assert len(r1.warnings) == 1
    assert len(r1.infos) == 1
    assert len(r1.messages) == 4
    assert r1.messages[0] == (ReportMessageType.ERROR, "fail")
    assert r1.messages[1] == (ReportMessageType.WARNING, "be careful")
    assert r1.messages[2] == (ReportMessageType.INFO, "info")
    assert r1.messages[3] == (ReportMessageType.ERROR, "another")

    assert len(r2.errors) == 1
    assert len(r2.warnings) == 0
    assert len(r2.infos) == 0
    assert len(r2.messages) == 1


def test_report_append():
    r = Report().append_error("e").append_info("i").append_warning("w")
    assert len(r.errors) == 1
    assert len(r.warnings) == 1
    assert len(r.infos) == 1
    assert len(r.messages) == 3
