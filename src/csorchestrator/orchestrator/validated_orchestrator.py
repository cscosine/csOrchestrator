from collections import Counter
from dataclasses import dataclass
from typing import TypeAlias

from csorchestrator.core.report import Report
from csorchestrator.core.result_with_report import ResultWithReport
from csorchestrator.orchestrator.orchestrator import Orchestrator


@dataclass(frozen=True)
class ValidatedOrchestrator:
    orchestrator: Orchestrator


ValidatedOrchestratorWithReport: TypeAlias = ResultWithReport[ValidatedOrchestrator]


def create_validated_orchestrator(o: Orchestrator) -> ValidatedOrchestratorWithReport:
    report = Report()

    # check phases name are unique
    phase_names = [p.name for p in o.phases]
    counter_phase_names = Counter(phase_names)
    for name, c in counter_phase_names.items():
        if c > 1:
            report.errors.append(f"phase named {name} has {c} occurrences")

    for p in o.phases:
        step_names = [s.name for s in p.steps]
        counter_step_names = Counter(step_names)
        for name, c in counter_step_names.items():
            if c > 1:
                report.errors.append(f"in phase {p.name}, step named {name} has {c} occurrences")

    if len(report.errors) > 0:
        return ValidatedOrchestratorWithReport.createReport(report)
    return ValidatedOrchestratorWithReport.createResultAndReport(ValidatedOrchestrator(o), report)
