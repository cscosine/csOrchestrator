from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.foundation.core.report import Report, ReportMessageType
from csorchestrator.frontend.reporters.reporter_sink_print import ReporterSinkPrint


def repo_to_reporter_sink(report: Report, reporter_sink: ReporterSinkBase | None = None) -> None:
    if reporter_sink is None:
        reporter_sink = ReporterSinkPrint()

    for t, m in report.messages:
        if t == ReportMessageType.ERROR:
            reporter_sink.error(f"{m}")
        elif t == ReportMessageType.WARNING:
            reporter_sink.warning(f"{m}")
        elif t == ReportMessageType.INFO:
            reporter_sink.info(f"{m}")
        else:
            reporter_sink.stderr(f"[Unkown report type {t}], message {m}")
