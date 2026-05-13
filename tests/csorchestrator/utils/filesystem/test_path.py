import platform
from pathlib import Path

import pytest

from csorchestrator.utils.file_system.path import is_clean_relative_path, try_parse_clean_relative_path


# run on windows
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-only test")
def test_is_clean_relative_path_win() -> None:
    assert not is_clean_relative_path("C:\\Users\\file.txt", avoid_leaving_base=False)  # Windows absolute
    assert try_parse_clean_relative_path("C:\\Users\\file.txt", avoid_leaving_base=False) is None


# run on linux/macOS
@pytest.mark.skipif(platform.system() == "Windows", reason="Windows absolute path test")
def test_is_clean_relative_path_non_win() -> None:
    assert not is_clean_relative_path("/", avoid_leaving_base=False)
    assert not is_clean_relative_path("/home/user/file.txt", avoid_leaving_base=False)  # Linux/macOS absolute

    assert try_parse_clean_relative_path("/", avoid_leaving_base=False) is None
    assert try_parse_clean_relative_path("/home/user/file.txt", avoid_leaving_base=False) is None


def test_is_clean_relative_path() -> None:

    # valid relative paths
    assert is_clean_relative_path("", avoid_leaving_base=False)
    assert is_clean_relative_path("./", avoid_leaving_base=False)
    assert is_clean_relative_path("relative", avoid_leaving_base=False)
    assert is_clean_relative_path("data/file.txt", avoid_leaving_base=False)
    assert is_clean_relative_path("./data", avoid_leaving_base=False)
    assert is_clean_relative_path("../data", avoid_leaving_base=False)
    assert is_clean_relative_path("folder/subfolder/file", avoid_leaving_base=False)

    # invalid relative paths
    assert try_parse_clean_relative_path("", avoid_leaving_base=False) is not None
    assert try_parse_clean_relative_path("./", avoid_leaving_base=False) is not None
    assert try_parse_clean_relative_path("relative", avoid_leaving_base=False) is not None
    assert try_parse_clean_relative_path("data/file.txt", avoid_leaving_base=False) is not None
    assert try_parse_clean_relative_path("./data", avoid_leaving_base=False) is not None
    assert try_parse_clean_relative_path("../data", avoid_leaving_base=False) is not None
    assert try_parse_clean_relative_path("folder/subfolder/file", avoid_leaving_base=False) is not None

    # invalid paths with avoid_leaving_base=True
    assert not is_clean_relative_path("../data", avoid_leaving_base=True)
    assert try_parse_clean_relative_path("../data", avoid_leaving_base=True) is None

    assert not is_clean_relative_path("data/../..", avoid_leaving_base=True)
    assert try_parse_clean_relative_path("data/../..", avoid_leaving_base=True) is None

    # same are ok with avoid_leaving_base=True
    assert is_clean_relative_path("../data", avoid_leaving_base=False)
    assert try_parse_clean_relative_path("../data", avoid_leaving_base=False) is not None

    assert is_clean_relative_path("data/../..", avoid_leaving_base=False)
    assert try_parse_clean_relative_path("data/../..", avoid_leaving_base=False) is not None

    # is ok to have a path that tries to leave the base but is actually ok because it doesn't leave the base
    assert is_clean_relative_path("data/../", avoid_leaving_base=True)
    assert try_parse_clean_relative_path("data/../", avoid_leaving_base=True) is not None


def test_resolve_exception_try_parse_clean_relative_path(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(self, *args, **kwargs):
        raise OSError("forced failure")

    monkeypatch.setattr(Path, "resolve", boom)

    result = try_parse_clean_relative_path(
        "some/path",
        avoid_leaving_base=True,
    )

    assert result is None
