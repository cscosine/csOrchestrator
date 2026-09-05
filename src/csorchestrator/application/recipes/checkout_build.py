from pathlib import Path
from typing import Final

from csorchestrator.domain.orchestrator.orchestrator import Orchestrator
from csorchestrator.foundation.git.resolve_url import RepoUrlParts
from csorchestrator.frontend.cscmake_presets.supported_variants import BuildConfig
from csorchestrator.frontend.local_execution.step_utils import StepExecuteOnlyOncePerMatrix
from csorchestrator.frontend.step.step_cmake_command import StepCMakeWorkflow
from csorchestrator.frontend.step.step_create_archives import StepCreateArchives
from csorchestrator.frontend.step.step_get_repository import (
    StepGetRepositoryExtraAccessToken,
    StepGetRepositoryExtraDepthOne,
    StepGetRepositoryGitHub,
    StepGetRepositoryGitHubSelf,
)
from csorchestrator.frontend.step.step_get_versions_from_cmake_config_package_version import (
    StepGetVersionsFromCMakeConfigPackageVersion,
)
from csorchestrator.frontend.step.step_upload_artifacts import (
    StepUploadArtifacts,
    create_artifact_prefix_from_orchestrator_name_version,
)
from csorchestrator.portable.package_version import CMakeConfigPackageVersionGrep, PackageVersion


class _All:
    pass


ALL: Final = _All()


def checkout_and_build_repos(
    orchestrator: Orchestrator,
    base_target_dir: Path,
    base_install_dir: Path,
    checkout_phase_name: str = "Repos Update",
    build_phase_name: str = "Configure-Build-Test-Install",
    create_artifact_phase_name: str = "Create and Upload Artifacts",
    repo_ref_build_type_list: dict[str, tuple[str, BuildConfig | None]] | None = None,
    checkout_self: bool = True,
    build_self: BuildConfig | None = None,
    repo_access_token: str | None = None,
    repos_auto_search_list: list[str] | _All | None = ALL,
    repos_config_file_list: list[CMakeConfigPackageVersionGrep] | None = None,
    repos_version_list: list[PackageVersion] | None = None,
) -> None:
    if repo_ref_build_type_list is None:
        repo_ref_build_type_list = {}

    p = orchestrator.create_phase(checkout_phase_name)

    # checkout myself for github actions
    if checkout_self:
        p.add_step(
            StepGetRepositoryGitHubSelf(
                name="3rdPartyBaseLibs git self-checkout",
                description="Checkout self repository",
            )
        )

    for repo, (repo_ref, _) in repo_ref_build_type_list.items():
        s = (
            StepGetRepositoryGitHub(
                name=f"{repo} Git clone/pull-ff",
                description=f"Clone or pull-ff {repo} description",
                target_directory=(base_target_dir / repo).as_posix(),
                repo_url_parts=RepoUrlParts(
                    repo_base_url=StepGetRepositoryGitHub.GITHUB_BASE_URL_SSH,
                    repo_org="cscosine",
                    repo_name=repo + ".git",
                ),
                repo_ref=repo_ref,
            )
            .add_extra(
                StepGetRepositoryExtraDepthOne(
                    on_local_checkout=False,
                    on_github_action_checkout=True,
                )
            )
            .add_extra(StepExecuteOnlyOncePerMatrix())
        )

        if repo_access_token is not None:
            s.add_extra(StepGetRepositoryExtraAccessToken(repo_access_token))

        p.add_step(s)

    # ----------------------------------------------------------------
    p = orchestrator.create_phase(build_phase_name)

    if build_self is not None:
        p.add_step(
            StepCMakeWorkflow(
                name="./ CMake Workflow",
                description="CMake workflow for ./",
                source_dir=Path("./").as_posix(),
                config=build_self,
            )
        )

    for repo, (_, config) in repo_ref_build_type_list.items():
        if config is not None:
            p.add_step(
                StepCMakeWorkflow(
                    name=f"{repo} CMake Workflow",
                    description=f"CMake workflow for {repo} with config: {config}",
                    source_dir=(base_target_dir / repo).as_posix(),
                    config=config,
                )
            )

    # ----------------------------------------------------------------
    p = orchestrator.create_phase(create_artifact_phase_name)

    repos_auto_search_list_value: list[str] = []
    if isinstance(repos_auto_search_list, _All):
        repos_auto_search_list_value = [
            repo for repo, (_, config) in repo_ref_build_type_list.items() if config is not None
        ]
    elif repos_auto_search_list is not None:
        repos_auto_search_list_value = repos_auto_search_list

    repos_config_file_list_value: list[CMakeConfigPackageVersionGrep] = []
    if repos_config_file_list is not None:
        repos_config_file_list_value = repos_config_file_list

    # repos_version: list[PackageVersion] | _All | None = (None,)
    repos_version_list_value: list[PackageVersion] = []
    if repos_version_list is not None:
        repos_version_list_value = repos_version_list

    p.add_step(
        StepGetVersionsFromCMakeConfigPackageVersion(
            name="Get Versions",
            description="Get Versions for all libs",
            repos_auto_search_list=repos_auto_search_list_value,
            repos_config_file_list=repos_config_file_list_value,
            repos_version=repos_version_list_value,
            base_install_dir=base_install_dir,
        )
    )

    p.add_step(
        StepCreateArchives(
            name="Create Archives",
            description="Create archives with libs and versions",
            base_install_dir=base_install_dir,
        )  # .add_extra(StepSkipExecutionOnLocal())
    )

    p.add_step(
        StepUploadArtifacts(
            name="Upload Artifacts",
            description="Upload Artifacts with libs and versions",
            base_install_dir=base_install_dir,
            artifact_prefix=create_artifact_prefix_from_orchestrator_name_version(orchestrator),
        )
    )
