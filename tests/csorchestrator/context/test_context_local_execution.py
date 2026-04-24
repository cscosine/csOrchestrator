from csorchestrator.context.context_local_execution import create_context_local_execution


def test_create_context_empty_path_invalid() -> None:
    cr = create_context_local_execution("")
    assert not cr.has_result()
    assert cr.report.has_errors()


def test_local_path(tmp_path, monkeypatch) -> None:
    # change local directory to tmp_path
    monkeypatch.chdir(tmp_path)

    cr = create_context_local_execution("./")

    assert cr.has_result()
    assert not cr.report.has_errors()
    assert cr.result().base_folder_path == tmp_path.resolve()
