from pathlib import Path


def is_clean_relative_path(path_str: str, avoid_leaving_base: bool) -> bool:
    p = Path(path_str)

    if p.is_absolute():
        return False

    if avoid_leaving_base:
        try:
            base = Path(".")
            base_resolved = base.resolve()
            resolved = (base_resolved / p).resolve()
        except Exception:
            return False

        if not resolved.is_relative_to(base_resolved):
            return False

    return True
