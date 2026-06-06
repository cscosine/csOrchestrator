from dataclasses import dataclass, field

from csorchestrator.context.context_local_execution import ContextLocalExecution, ContextLocalExecutionExtra
from csorchestrator.context.context_os_architecture import OS
from csorchestrator.orchestrator.step_base import StepExtra


@dataclass
class StepExecuteOnlyOncePerMatrix(StepExtra):
    # return none if the step should be executed,
    # otherwise return a string with the reason why it should not be executed
    def evaluate_local_exec(
        self, context: ContextLocalExecution, current_phase_name: str, step_name: str
    ) -> None | str:
        matrix_extra = context.get_matrix_extra(StepGetRepositoryExecuteOnlyOncePerMatrixContextLocalExecutionExtra)

        if matrix_extra is None:
            matrix_extra = StepGetRepositoryExecuteOnlyOncePerMatrixContextLocalExecutionExtra()
            context.add_matrix_extra(matrix_extra)

        if (current_phase_name, step_name) in matrix_extra.already_executed_on_phase_step:
            return "Step is already executed on this matrix"

        matrix_extra.already_executed_on_phase_step.add((current_phase_name, step_name))
        return None


@dataclass
class StepGetRepositoryExecuteOnlyOncePerMatrixContextLocalExecutionExtra(ContextLocalExecutionExtra):
    already_executed_on_phase_step: set[tuple[str, str]] = field(default_factory=set)


@dataclass
class StepSkipExecutionOnLocal(StepExtra):
    pass


@dataclass
class StepExecuteOnlyOn(StepExtra):
    os: OS
    version_starts_with: str | None = None  # if None, any version is valid

    # return none if the step should be executed,
    # otherwise return a string with the reason why it should not be executed
    def evaluate_local_exec(self, context: ContextLocalExecution) -> None | str:
        if context.os_architecture.os != self.os:
            return f"Step is marked to be executed only on {self.os.value} but current OS is {context.os_architecture.os.value}"  # noqa: E501
        if self.version_starts_with is not None and not context.os_architecture.os_version.startswith(
            self.version_starts_with
        ):
            return f"Step is marked to be executed only on {self.os.value} with version starting with {self.version_starts_with} but current version is {context.os_architecture.os_version}"  # noqa: E501
        return None
