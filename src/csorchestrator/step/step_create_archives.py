import json
import tarfile
from dataclasses import dataclass
from pathlib import Path

from csorchestrator.ci.github.github_workflow_steps_transations import StepRunCommand
from csorchestrator.ci.github.guthub_workflow_matrix_constants import (
    create_context_os_architecture_compiler_generator_string_github_matrix,
)
from csorchestrator.context.context_local_execution import (
    ContextLocalExecution,
)
from csorchestrator.context.context_os_architecture_compiler_generator import (
    create_context_os_architecture_compiler_generator_string,
)
from csorchestrator.domain.orchestrator.reporter_sink_base import ReporterSinkBase
from csorchestrator.domain.orchestrator.step_base import (
    JobOrchestratorMatrixExecution,
    StepBase,
    StepValidatorBase,
    StepValidatorNoOp,
)
from csorchestrator.foundation.core.report import Report


@dataclass
class StepCreateArchives(StepBase):
    input_id: str
    input_dict: str
    base_install_dir: Path

    def execute_locally(self, context: ContextLocalExecution, reporter_sink: ReporterSinkBase) -> Report:
        return execute_step_create_archives(self, context, reporter_sink)

    def to_githubwf(self, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase) -> Report:
        return step_create_archives_to_githubwf(self, wf_job, reporter_sink)

    @classmethod
    def createValidator(cls) -> StepValidatorBase:
        return StepValidatorNoOp()


def execute_step_create_archives(
    step: StepCreateArchives, context: ContextLocalExecution, reporter_sink: ReporterSinkBase
) -> Report:
    report = Report()

    install_subdir = create_context_os_architecture_compiler_generator_string(
        context.get_active_os_architecture_compiler_generator()
    )
    input_full_dir = Path(context.base_folder_path / step.base_install_dir / install_subdir).resolve()
    input_full_path = Path(input_full_dir / Path(step.input_id + ".ver")).resolve()

    packages = None
    with open(input_full_path) as f:
        line = f.read().strip()
        key, value = line.split("=", 1)
        if key != step.input_dict:
            report.append_error(f"unexpected key {key} in {str(input_full_path)}, expected {step.input_dict}")
            return report
        packages = json.loads(value)

    assert packages is not None

    for item in packages:
        name = item["name"]
        version = item["version"]
        input_path = Path(input_full_dir / Path(name)).resolve()
        output_path = Path(
            input_full_dir / Path(str(install_subdir) + "-" + name + "-" + version + ".tar.gz")
        ).resolve()

        report.append_info(f"tar.gz {str(input_path)} to {str(output_path)} ")
        with tarfile.open(output_path, "w:gz") as tar:
            for path in input_path.rglob("*"):
                resolved_path = path.resolve()
                arcname = path.resolve().relative_to(input_full_dir)
                tar.add(resolved_path, arcname=arcname)
    return report


def step_create_archives_to_githubwf(
    step: StepCreateArchives, wf_job: JobOrchestratorMatrixExecution, reporter_sink: ReporterSinkBase
) -> Report:

    install_dir_name = create_context_os_architecture_compiler_generator_string_github_matrix()
    install_subdir = step.base_install_dir / install_dir_name

    lines = [
        "import json",
        "import os",
        "import tarfile",
        "from pathlib import Path",
        "",
        "versions = json.loads(os.environ['VERSIONS'])",
        "",
        "for entry in versions:",
        "    name = entry['name']",
        "    version = entry['version']",
        f"    install_subdir = Path('{install_subdir.as_posix()}').resolve()",
        "    input_path = Path(install_subdir / Path(name)).resolve()",
        f"    output_path = Path(install_subdir / Path('{install_dir_name}' + '-' + name + '-' + version + '.tar.gz')).resolve()",  # noqa: E501
        "    ",
        "    with tarfile.open(output_path, 'w:gz') as tar:",
        "        for path in input_path.rglob('*'):",
        "            resolved_path = path.resolve()",
        "            arcname = path.resolve().relative_to(install_subdir)",
        "            tar.add(resolved_path, arcname=arcname)",
    ]

    # produce output
    run_str_list = ["|"] + lines

    wf_job.steps.append(
        StepRunCommand(
            name="Create Archives",
            shell_type="python",
            env=[f"VERSIONS: ${{{{ steps.{step.input_id}.outputs.{step.input_dict} }}}}"],
            run=run_str_list,
        )
    )

    return Report()
