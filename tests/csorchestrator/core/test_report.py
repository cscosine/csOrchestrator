from csorchestrator.core.report import Report


def test_report_append_and_print(capfd):
    r1 = Report()
    r1.errors.append("fail")
    assert len(r1.errors) == 1
    assert r1.has_errors()
    assert len(r1.warnings) == 0
    assert not r1.has_warnings()
    assert len(r1.infos) == 0
    assert not r1.has_info()

    r1.warnings.append("be careful")
    assert len(r1.errors) == 1
    assert r1.has_errors()
    assert len(r1.warnings) == 1
    assert r1.has_warnings()
    assert len(r1.infos) == 0
    assert not r1.has_info()

    r1.infos.append("info")
    assert len(r1.errors) == 1
    assert r1.has_errors()
    assert len(r1.warnings) == 1
    assert r1.has_warnings()
    assert len(r1.infos) == 1
    assert r1.has_info()

    r2 = Report()
    r2.errors.append("another")
    assert len(r2.errors) == 1
    assert len(r2.warnings) == 0
    assert len(r2.infos) == 0

    # merge reports
    r1.append_report(r2)
    assert len(r1.errors) == 2
    assert len(r1.warnings) == 1
    assert len(r1.infos) == 1

    assert len(r2.errors) == 1
    assert len(r2.warnings) == 0
    assert len(r2.infos) == 0

    # capture output
    r1.print()
    captured = capfd.readouterr()
    text = captured.out
    # remove ANSI escapes for easier assertions
    import re

    clean = re.sub(r"\x1b\[[0-9;]*m", "", text)

    assert "[ERROR] fail" in clean
    assert "[ERROR] another" in clean
    assert "[WARNING] be careful" in clean
    assert "[INFO] info" in clean

    # capture output
    r2.print()
    captured = capfd.readouterr()
    text = captured.out
    # remove ANSI escapes for easier assertions
    import re

    clean = re.sub(r"\x1b\[[0-9;]*m", "", text)

    assert "[ERROR] another" in clean

    # printing empty report should be silent
    empty = Report()
    empty.print()
    captured = capfd.readouterr()
    assert captured.out == ""


def test_report_append():
    r = Report().append_error("e").append_info("i").append_warning("w")
    assert len(r.errors) == 1
    assert len(r.warnings) == 1
    assert len(r.infos) == 1
