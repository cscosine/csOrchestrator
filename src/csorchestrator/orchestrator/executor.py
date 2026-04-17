from dataclasses import dataclass

from csorchestrator.orchestrator.orchestrator import Orchestrator


@dataclass
class Executor:
    orchestrator: Orchestrator


#     def execute(self):
#         for phase in self.orchestrator.phases:
#             print(f"Executing phase: {phase.name}")
#             for step in phase.steps:
#                 print(f"  Executing step: {step.name}")
#                 step.execute()
