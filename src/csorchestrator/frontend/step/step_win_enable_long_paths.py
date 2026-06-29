from dataclasses import dataclass

from csorchestrator.frontend.step.step_custom_command import StepWinPSCommand


@dataclass
class StepWinEnableLongPaths(StepWinPSCommand):
    def __post_init__(self) -> None:
        super().__post_init__()  # call parent

        script = [
            "Set-ItemProperty `",
            ' -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem" `',
            " -Name LongPathsEnabled `",
            " -Value 1",
            "",
            '$v = [int](Get-ItemProperty "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem").LongPathsEnabled',
            "if ($v -ne 1) {",
            '    throw "LongPathsEnabled is NOT enabled (value = $v)"',
            "}",
        ]

        self.cmd = script
