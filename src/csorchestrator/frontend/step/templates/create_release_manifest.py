import sys
from pathlib import Path
from typing import cast

from csorchestrator.portable.release_manifest import (
    collect_release_manifest_single_variant_and_prepare_manifest,
)

input_manifest_path_variant = cast(list[tuple[Path, str]], "__INPUT_MANIFEST_PATH_VARIANT__")
output_filepath=cast(Path, "__OUTPUT_FILE_PATH__")  # fmt: skip
project_name = "__PROJECT_NAME__"
project_version = "__PROJECT_VERSION__"

errors_list = collect_release_manifest_single_variant_and_prepare_manifest(
    input_manifest_path_variant=input_manifest_path_variant,
    output_filepath=output_filepath,
    project_name=project_name,
    project_version=project_version,
)

if len(errors_list) > 0:
    for e in errors_list:
        print(e)
    sys.exit("ERROR: getting package versions")
