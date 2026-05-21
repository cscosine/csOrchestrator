from csorchestrator.core.report import Report
from csorchestrator.reporters.report_reporter import repo_to_reporter_sink
from csorchestrator.reporters.reporter_sink_colored_print import ReporterSinkColoredPrint


def test_report_reporter():
    r = Report()
    r.append_error("E")
    r.append_warning("W")
    r.append_warning("I")
    # add unsupported message
    r._messages.append(["INVALID", "INVALID"])  # type: ignore[arg-type]

    repo_to_reporter_sink(r)  # report on print

    repo_to_reporter_sink(r, ReporterSinkColoredPrint())
