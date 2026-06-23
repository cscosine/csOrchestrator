from csorchestrator.orchestrator.step_base import JobOrchestratorMatrixExecution, JobStrategy
from csorchestrator.orchestrator.workflow_config import MatrixOsArchCompilerGeneratorRunnerEntryInclude
from csorchestrator.utils.common.strings import string_indent


def job_strategy_to_string_lines(jobStrategy: JobStrategy, indent: int = 0) -> list[str]:
    fail_fast_str = str(jobStrategy.fail_fast).lower()
    line_list = [
        f"{string_indent(indent)}strategy:",
        f"{string_indent(indent + 2)}fail-fast: {fail_fast_str}",
    ]
    if len(jobStrategy._matrix_includes) > 0:
        line_list.append(f"{string_indent(indent + 2)}matrix:")
        line_list.append(f"{string_indent(indent + 4)}include:")
        for matrix_include in jobStrategy._matrix_includes:
            line_list += matrix_to_string_lines(matrix_include, indent + 6)
    return line_list


def job_orchestrator_matrix_execution_to_string_lines(
    jme: JobOrchestratorMatrixExecution, indent: int = 0
) -> list[str]:
    line_list = [f"{string_indent(indent)}{jme.name}:", f"{string_indent(indent + 2)}runs-on: {jme.runs_on}", ""]
    line_list += job_strategy_to_string_lines(jme.strategy, indent + 2)
    line_list += [""]
    if len(jme.steps) > 0:
        line_list += [f"{string_indent(indent + 2)}steps:"]
        for step in jme.steps:
            line_list += step.to_string_lines(indent + 4)
            line_list += [""]

    return line_list


def matrix_to_string_lines(mat: MatrixOsArchCompilerGeneratorRunnerEntryInclude, indent: int = 0) -> list[str]:
    list_str = [
        f"{string_indent(indent)}- execution_id: {mat.execution_id}",
        f"{string_indent(indent)}  os: {mat.os}",
        f"{string_indent(indent)}  os_version: {mat.os_version}",
        f"{string_indent(indent)}  architecture: {mat.architecture}",
        f"{string_indent(indent)}  architecture_variant: {mat.architecture_variant}",
        f"{string_indent(indent)}  compiler: {mat.compiler}",
    ]

    if mat.c_compiler is not None:
        list_str += [
            f"{string_indent(indent)}  c_compiler: {mat.c_compiler}",
        ]

    if mat.cpp_compiler is not None:
        list_str += [
            f"{string_indent(indent)}  cpp_compiler: {mat.cpp_compiler}",
        ]

    if mat.toolset is not None:
        list_str += [
            f"{string_indent(indent)}  toolset: {mat.toolset}",
        ]

    list_str += [
        f"{string_indent(indent)}  compiler_version: {mat.compiler_version}",
        f"{string_indent(indent)}  generator: {mat.build_generator}",
        f"{string_indent(indent)}  generator_type: {mat.build_generator_type}",
        f"{string_indent(indent)}  generator_cmake: {mat.generator_cmake}",
        f"{string_indent(indent)}  runner: {mat.runner}",
    ]
    return list_str
