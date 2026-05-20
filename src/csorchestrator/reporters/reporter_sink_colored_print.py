from dataclasses import dataclass

from csorchestrator.reporters.reporter_sink_print import ReporterSinkPrintBase


class Ansi:
    RESET = "\033[0m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"


@dataclass
class ReporterSinkColoredPrint(ReporterSinkPrintBase):
    indentation: str = ""

    def reset_indentation(self) -> None:
        self.indentation = ""

    def increase_indentation(self) -> None:
        self.indentation += "  "

    def decrease_indentation(self) -> None:
        self.indentation = self.indentation[:-2]

    def _print(self, prefix: str, text: str, color: str = "") -> None:
        prefix_str = f"{self.indentation}{color}{prefix}{Ansi.RESET} "
        padding = " " * len(self.indentation + prefix + " ")

        lines = text.splitlines() or [""]

        for i, line in enumerate(lines):
            if i == 0:
                print(f"{prefix_str}{line}{Ansi.RESET}")
            else:
                print(f"{padding}{line}")

    def stdout(self, text: str) -> None:
        self._print("[cout]", text, Ansi.CYAN)

    def stderr(self, text: str) -> None:
        self._print("[cerr]", text, Ansi.RED)

    def info(self, text: str) -> None:
        self._print("[info]", text, Ansi.BLUE)

    def warning(self, text: str) -> None:
        self._print("[warning]", text, Ansi.YELLOW)

    def error(self, text: str) -> None:
        self._print("[error]", text, Ansi.RED)
