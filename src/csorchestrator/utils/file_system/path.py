from pathlib import Path
from typing import Optional


def is_clean_relative_path(path_str: str) -> bool:
    op = try_parse_clean_relative_path(path_str)
    if op is not None:
        return True
    return False


def try_parse_clean_relative_path(path_str: str) -> Optional[Path]:
    p = Path(path_str)

    if p.is_absolute():
        return None

    return p
