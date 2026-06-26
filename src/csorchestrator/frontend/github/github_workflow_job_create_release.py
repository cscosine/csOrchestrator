from dataclasses import dataclass

from csorchestrator.foundation.core.strings_utils import string_indent


@dataclass
class JobReleaseCreationFromArifacts:
    name: str
    needs: str
    runs_on: str
    if_str: str


def job_release_on_tag_to_string_lines(job: JobReleaseCreationFromArifacts, indent: int = 0) -> list[str]:
    line_list = [f"{string_indent(indent)}{job.name}:"]
    line_list += [f"{string_indent(indent + 2)}needs: {job.needs}"]
    line_list += [f"{string_indent(indent + 2)}runs-on: {job.runs_on}"]
    line_list += [""]
    line_list += [f"{string_indent(indent + 2)}if: {job.if_str}"]
    line_list += [""]
    line_list += [f"{string_indent(indent + 2)}permissions:"]
    line_list += [f"{string_indent(indent + 4)}contents: write"]
    line_list += [""]
    line_list += [f"{string_indent(indent + 2)}steps:"]
    line_list += [f"{string_indent(indent + 4)}- name: Download all artifacts"]
    line_list += [f"{string_indent(indent + 6)}uses: actions/download-artifact@v8"]
    line_list += [f"{string_indent(indent + 6)}with:"]
    line_list += [f"{string_indent(indent + 8)}path: artifacts"]
    line_list += [""]
    line_list += [f"{string_indent(indent + 4)}- name: Show downloaded files"]
    line_list += [f"{string_indent(indent + 6)}run: find artifacts -type f"]
    line_list += [""]
    line_list += [f"{string_indent(indent + 4)}- name: Create GitHub Release"]
    line_list += [f"{string_indent(indent + 6)}uses: softprops/action-gh-release@v3"]
    line_list += [f"{string_indent(indent + 6)}with:"]
    line_list += [f"{string_indent(indent + 8)}files: |"]
    line_list += [f"{string_indent(indent + 10)}artifacts/**/*    "]
    line_list += [""]
    return line_list
