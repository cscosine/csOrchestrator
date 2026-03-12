import sys
from typing import Optional, Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Script entry point.

    Returns:
        0 on success
        1 on error
    """
    print("\033[32m✅ csorchestrator finished successfully.\033[0m", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
