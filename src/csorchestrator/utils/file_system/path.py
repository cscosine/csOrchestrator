from pathlib import Path


def is_clean_relative_path(path_str: str, avoid_leaving_base: bool) -> bool:
    op = try_parse_clean_relative_path(path_str, avoid_leaving_base)
    if op is not None:
        return True
    return False


def try_parse_clean_relative_path(path_str: str, avoid_leaving_base: bool) -> Path | None:
    p = Path(path_str)

    if p.is_absolute():
        return None

    if avoid_leaving_base:
        try:
            base = Path(".")
            base_resolved = base.resolve()
            resolved = (base_resolved / p).resolve()
        except Exception:
            return None

        if not resolved.is_relative_to(base_resolved):
            return None

        return resolved
    else:
        return p.resolve()


def resolve_path(path_str: str) -> Path:
    p = Path(path_str)
    return p.resolve()
