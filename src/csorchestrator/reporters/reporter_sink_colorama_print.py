from dataclasses import dataclass

from colorama import Fore, Style, init

from csorchestrator.reporters.reporter_sink_print import ReporterSinkPrintBase

init()  # enables ANSI on Windows cmd


@dataclass
class ReporterSinkColoramaPrint(ReporterSinkPrintBase):
    indentation: str = ""

    def reset_indentation(self) -> None:
        self.indentation = ""

    def increase_indentation(self) -> None:
        self.indentation += "  "

    def decrease_indentation(self) -> None:
        self.indentation = self.indentation[:-2]

    def _print(self, prefix: str, text: str, color: str = "") -> None:
        prefix_str = f"{self.indentation}{color}{prefix}{Style.RESET_ALL} "
        padding = " " * len(self.indentation + prefix + " ")

        for i, line in enumerate(text.splitlines() or [""]):
            if i == 0:
                print(f"{prefix_str}{line}{Style.RESET_ALL}")
            else:
                print(f"{padding}{line}")

    def stdout(self, text: str) -> None:
        self._print("[cout]", text, Fore.CYAN)

    def stderr(self, text: str) -> None:
        self._print("[cerr]", text, Fore.RED)

    def info(self, text: str) -> None:
        self._print("[info]", text, Fore.BLUE)

    def warning(self, text: str) -> None:
        self._print("[warning]", text, Fore.YELLOW)

    def error(self, text: str) -> None:
        self._print("[error]", text, Fore.RED)
