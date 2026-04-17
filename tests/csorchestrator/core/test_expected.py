from csorchestrator.core.expected import Expected


def test_expected_ok() -> None:
    e = Expected(value=42)
    assert e.is_ok
    assert e.value == 42
    assert e.error is None


def test_expected_error() -> None:
    e = Expected(error="fail")
    assert e.is_error
    assert e.error == "fail"
    assert e.value is None
