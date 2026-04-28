import sys
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
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
