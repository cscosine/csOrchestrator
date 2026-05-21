import sys
from unittest.mock import patch

import pytest

from csorchestrator.reporters.reporter_sink_colorama_print import ReporterSinkColoramaPrint
from csorchestrator.reporters.reporter_sink_colored_print import ReporterSinkColoredPrint


@pytest.mark.parametrize("sink_class", [ReporterSinkColoredPrint, ReporterSinkColoramaPrint])
def test_colored_sinks_output_ansi_codes(capsys: pytest.CaptureFixture[str], sink_class: type) -> None:
    with patch.object(sys.stdout, "isatty", return_value=True):
        sink = sink_class()

        # Test Info (usually blue/cyan)
        sink.info("Colored Message")
        captured = capsys.readouterr()
        all_output = captured.out + captured.err
        assert "Colored Message" in all_output
        # Check for the existence of ANSI escape characters
        assert "\x1b" in all_output or "\033" in all_output


def test_colored_sink_error_output(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys.stderr, "isatty", return_value=True):
        sink = ReporterSinkColoredPrint()

        sink.error("Fatal Error")
        captured = capsys.readouterr()
        all_output = captured.out + captured.err

        assert "Fatal Error" in all_output
        # Ensure it's prefixed or wrapped in codes (specifically 31 for Red often)
        assert "[error]" in all_output
