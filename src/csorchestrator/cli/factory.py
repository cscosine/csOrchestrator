from typing import TypeAlias

from csorchestrator.context.context_os_architecture_compiler_generator import ExecutionMatrixOsArchCompilerGenerator
from csorchestrator.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.orchestrator.orchestrator import Orchestrator
from csorchestrator.utils.presets.supported_variants import get_supported_context_os_architecture_list


def create_orchestrator_factory(name: str, version: str, execution_matrix_name: str) -> Orchestrator:
    return Orchestrator(
        name=name,
        version=version,
        execution_matrix=ExecutionMatrixOsArchCompilerGenerator(execution_matrix_name),
    )


def create_orchestrator_factory_all_supported_cases(
    name: str,
    version: str,
    execution_matrix_name: str,
    use_ninja_for_windows: bool = False,
    use_ninja: bool = True,
    use_ninjamulti: bool = True,
) -> Orchestrator:
    o = create_orchestrator_factory(
        name=name,
        version=version,
        execution_matrix_name=execution_matrix_name,
    )
    o.set_execution_matrix_list(
        get_supported_context_os_architecture_list(
            use_ninja_for_windows=use_ninja_for_windows,
            use_ninja=use_ninja,
            use_ninjamulti=use_ninjamulti,
        )
    )
    return o


OptionalOrchestratorWithReport: TypeAlias = OptionalResultWithReport[Orchestrator]
