import os

import pytest

from csorchestrator.utils.file_system.path import is_clean_relative_path, try_parse_clean_relative_path


# run on windows
@pytest.mark.skipif(os.name != "nt", reason="Windows absolute path test")
def test_is_clean_relative_path_win() -> None:
    assert not is_clean_relative_path("C:\\Users\\file.txt")  # Windows absolute
    assert try_parse_clean_relative_path("C:\\Users\\file.txt") is None


# run on linux/macOS
@pytest.mark.skipif(os.name == "nt", reason="Windows absolute path test")
def test_is_clean_relative_path_non_win() -> None:
    assert not is_clean_relative_path("/")
    assert not is_clean_relative_path("/home/user/file.txt")  # Linux/macOS absolute

    assert try_parse_clean_relative_path("/") is None
    assert try_parse_clean_relative_path("/home/user/file.txt") is None


def test_is_clean_relative_path() -> None:

    assert is_clean_relative_path("")
    assert is_clean_relative_path("./")
    assert is_clean_relative_path("relative")
    assert is_clean_relative_path("data/file.txt")
    assert is_clean_relative_path("./data")
    assert is_clean_relative_path("../data")
    assert is_clean_relative_path("folder/subfolder/file")

    assert try_parse_clean_relative_path("") is not None
    assert try_parse_clean_relative_path("./") is not None
    assert try_parse_clean_relative_path("relative") is not None
    assert try_parse_clean_relative_path("data/file.txt") is not None
    assert try_parse_clean_relative_path("./data") is not None
    assert try_parse_clean_relative_path("../data") is not None
    assert try_parse_clean_relative_path("folder/subfolder/file") is not None
