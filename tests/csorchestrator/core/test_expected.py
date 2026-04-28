from csorchestrator.core.expected import Expected


def test_expected_ok() -> None:
    e = Expected(value=42)
    assert e.is_ok
    assert e.value == 42
    assert e.error is None

    e = Expected.make_value(42)
    assert e.is_ok
    assert e.value == 42
    assert e.error is None


def test_expected_error() -> None:
    e = Expected(error="fail")
    assert e.is_error
    assert e.error == "fail"
    assert e.value is None

    e = Expected.make_error("fail")
    assert e.is_error
    assert e.error == "fail"
    assert e.value is None


def test_expected_raise() -> None:
    unexpected_success = False
    try:
        _ = Expected()
        unexpected_success = True
    except ValueError:
        assert True

    assert not unexpected_success

    try:
        _ = Expected(error=42, value=23)
        unexpected_success = True
    except ValueError:
        assert True

    assert not unexpected_success
