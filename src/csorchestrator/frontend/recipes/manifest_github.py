import os
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias
from urllib import request
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin

from csorchestrator.foundation.core.optional_result_with_report import OptionalResultWithReport
from csorchestrator.foundation.core.report import Report
from csorchestrator.foundation.file_system.directory import ensure_directory_exists_or_create_and_is_usable
from csorchestrator.frontend.step.step_get_repository import StepGetRepositoryGitHub
from csorchestrator.portable.release_manifest import ReleaseManifest


@dataclass(frozen=True)
class ManifestGithub:
    base_url: str
    org: str
    project_name: str
    project_version: str
    release_tag: str

    GITHUB_BASE_URL_HTTPS: str = StepGetRepositoryGitHub.GITHUB_BASE_URL_HTTPS

    # TODO for private repo, will need to use API url and a api request to download, using a toke,
    # with keyring in local and token in github


OptionalManifestPathWithReport: TypeAlias = OptionalResultWithReport[Path]


def download_manifest(manifest_description: ManifestGithub, output_folder: Path) -> OptionalManifestPathWithReport:
    report = Report()

    dir_creation_res = ensure_directory_exists_or_create_and_is_usable(str(output_folder.resolve()))

    if dir_creation_res.error is not None:
        report.append_error(dir_creation_res.error)
        return OptionalManifestPathWithReport.createReport(report)

    assert dir_creation_res.value is not None
    target_dir = dir_creation_res.value

    # TODO not great to join with "-" here
    source_filename = (
        manifest_description.project_name
        + "-"
        + manifest_description.project_version
        + ReleaseManifest.CS_ORCHESTRATOR_MANIFEST_EXTENSION
    )
    target_filename = target_dir / source_filename

    download_url = urljoin(
        manifest_description.base_url,
        "/".join(
            [
                manifest_description.org,
                manifest_description.project_name,
                "releases",
                "download",
                manifest_description.release_tag,
                source_filename,
            ]
        ),
    )
    report.append_info("download URL " + download_url + " to " + target_filename.as_posix())

    # download
    try:
        request.urlretrieve(download_url, target_filename)
    except HTTPError as e:
        report.append_error(f"HTTP error: {e.code} - {e.reason}")
        return OptionalManifestPathWithReport.createReport(report)

    except URLError as e:
        report.append_error(f"Network error: {e.reason}")
        return OptionalManifestPathWithReport.createReport(report)

    # Check file exists and is not empty
    if not os.path.exists(target_filename):
        report.append_error("Download failed: file does not exist")
        return OptionalManifestPathWithReport.createReport(report)

    if os.path.getsize(target_filename) == 0:
        report.append_error("Download failed: file is empty")
        return OptionalManifestPathWithReport.createReport(report)

    return OptionalManifestPathWithReport.createResultAndReport(target_filename, report)
