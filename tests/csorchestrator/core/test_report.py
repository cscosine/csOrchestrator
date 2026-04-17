from csorchestrator.core.report import Report


def test_report_append_and_print(capfd):
    r1 = Report()
    r1.errors.append("fail")
    assert len(r1.errors) == 1
    assert len(r1.warnings) == 0
    assert len(r1.infos) == 0

    r1.warnings.append("be careful")
    assert len(r1.errors) == 1
    assert len(r1.warnings) == 1
    assert len(r1.infos) == 0

    r1.infos.append("info")
    assert len(r1.errors) == 1
    assert len(r1.warnings) == 1
    assert len(r1.infos) == 1

    r2 = Report()
    r2.errors.append("another")
    assert len(r2.errors) == 1
    assert len(r2.warnings) == 0
    assert len(r2.infos) == 0

    # merge reports
    r1.append(r2)
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

    # printing empty report should be silent
    empty = Report()
    empty.print()
    captured = capfd.readouterr()
    assert captured.out == ""
