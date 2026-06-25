import platform
from pathlib import Path

import pytest

from csorchestrator.context.context_os_architecture import OS
from csorchestrator.foundation.file_system.path import is_clean_relative_path


# run on WINDOWS
@pytest.mark.skipif(platform.system().lower() != OS.WINDOWS.value, reason=OS.WINDOWS.value + "-only test")
def test_is_clean_relative_path_win() -> None:
    assert not is_clean_relative_path("C:\\Users\\file.txt", avoid_leaving_base=False)  # absolute


# run on LINUX/MACOS
@pytest.mark.skipif(platform.system().lower() == OS.WINDOWS.value, reason=OS.WINDOWS.value + " absolute path test")
def test_is_clean_relative_path_non_win() -> None:
    assert not is_clean_relative_path("/", avoid_leaving_base=False)
    assert not is_clean_relative_path("/home/user/file.txt", avoid_leaving_base=False)  # LINUX/MACOS absolute


def test_is_clean_relative_path() -> None:

    # valid relative paths
    assert is_clean_relative_path("", avoid_leaving_base=False)
    assert is_clean_relative_path("./", avoid_leaving_base=False)
    assert is_clean_relative_path("relative", avoid_leaving_base=False)
    assert is_clean_relative_path("data/file.txt", avoid_leaving_base=False)
    assert is_clean_relative_path("./data", avoid_leaving_base=False)
    assert is_clean_relative_path("../data", avoid_leaving_base=False)
    assert is_clean_relative_path("folder/subfolder/file", avoid_leaving_base=False)

    # invalid paths with avoid_leaving_base=True
    assert not is_clean_relative_path("../data", avoid_leaving_base=True)

    assert not is_clean_relative_path("data/../..", avoid_leaving_base=True)

    # same are ok with avoid_leaving_base=True
    assert is_clean_relative_path("../data", avoid_leaving_base=False)

    assert is_clean_relative_path("data/../..", avoid_leaving_base=False)

    # is ok to have a path that tries to leave the base but is actually ok because it doesn't leave the base
    assert is_clean_relative_path("data/../", avoid_leaving_base=True)


def test_resolve_exception_is_clean_relative_path(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(self, *args, **kwargs):
        raise OSError("forced failure")

    monkeypatch.setattr(Path, "resolve", boom)

    assert not is_clean_relative_path(
        "some/path",
        avoid_leaving_base=True,
    )
