from csorchestrator.context.context_os_architecture import OS
from csorchestrator.utils.presets.supported_variants import (
    BuildConfig,
    GeneratorType,
    get_all_supported_workflow_descriptions,
    get_supported_context_os_architecture_config_list,
    get_supported_os_version_list,
    is_config_selected_multi_config_generator,
    is_config_selected_single_config_generator,
    workflow_name_from_description,
)


def test_get_supported_context_os_architecture_config_list():
    supported_list = get_supported_context_os_architecture_config_list()
    n_all = len(supported_list)
    assert n_all > 0

    supported_list = get_supported_context_os_architecture_config_list(GeneratorType.SINGLE_CONFIG)
    n_single = len(supported_list)

    assert n_single > 0
    assert n_single < n_all

    supported_list = get_supported_context_os_architecture_config_list(GeneratorType.MULTI_CONFIG)
    n_multi = len(supported_list)

    assert n_multi > 0
    assert n_multi < n_all

    supported_list = get_supported_context_os_architecture_config_list("INVALID")  # type: ignore
    n_invalid = len(supported_list)
    assert n_invalid == 0


def test_is_config_selected_multi_config_generator() -> None:

    assert is_config_selected_multi_config_generator(BuildConfig.DEBUG, BuildConfig.DEBUG)
    assert is_config_selected_multi_config_generator(BuildConfig.RELEASE, BuildConfig.RELEASE)
    assert is_config_selected_multi_config_generator(BuildConfig.RELWITHDEBINFO, BuildConfig.RELWITHDEBINFO)
    assert is_config_selected_multi_config_generator(BuildConfig.PARANOID, BuildConfig.PARANOID)
    assert is_config_selected_multi_config_generator(BuildConfig.DEBUG_RELEASE, BuildConfig.DEBUG_RELEASE)
    assert is_config_selected_multi_config_generator(
        BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID, BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID
    )

    assert not is_config_selected_multi_config_generator(BuildConfig.RELEASE, BuildConfig.DEBUG)
    assert not is_config_selected_multi_config_generator(BuildConfig.DEBUG_RELEASE, BuildConfig.DEBUG)
    assert not is_config_selected_multi_config_generator(BuildConfig.DEBUG_RELEASE, BuildConfig.RELEASE)

    assert not is_config_selected_multi_config_generator(current_config="INVALID", requested_config=BuildConfig.DEBUG)  # type: ignore
    assert not is_config_selected_multi_config_generator(current_config=BuildConfig.DEBUG, requested_config="INVALID")  # type: ignore
    assert not is_config_selected_multi_config_generator(current_config="INVALID", requested_config="INVALID")  # type: ignore


def test_is_config_selected_single_config_generator() -> None:

    # single config request are ok if they exactly match the current config
    assert is_config_selected_single_config_generator(
        current_config=BuildConfig.DEBUG, requested_config=BuildConfig.DEBUG
    )
    assert is_config_selected_single_config_generator(
        current_config=BuildConfig.RELEASE, requested_config=BuildConfig.RELEASE
    )
    assert is_config_selected_single_config_generator(
        current_config=BuildConfig.RELWITHDEBINFO, requested_config=BuildConfig.RELWITHDEBINFO
    )
    assert is_config_selected_single_config_generator(
        current_config=BuildConfig.PARANOID, requested_config=BuildConfig.PARANOID
    )

    assert not is_config_selected_single_config_generator(
        current_config=BuildConfig.DEBUG, requested_config=BuildConfig.RELEASE
    )
    assert not is_config_selected_single_config_generator(
        current_config=BuildConfig.RELWITHDEBINFO, requested_config=BuildConfig.PARANOID
    )

    # if we request debug release, both debug and release are ok
    assert is_config_selected_single_config_generator(
        current_config=BuildConfig.DEBUG, requested_config=BuildConfig.DEBUG_RELEASE
    )
    assert is_config_selected_single_config_generator(
        current_config=BuildConfig.RELEASE, requested_config=BuildConfig.DEBUG_RELEASE
    )
    assert not is_config_selected_single_config_generator(
        current_config=BuildConfig.PARANOID, requested_config=BuildConfig.DEBUG_RELEASE
    )
    assert not is_config_selected_single_config_generator(
        current_config=BuildConfig.RELWITHDEBINFO, requested_config=BuildConfig.DEBUG_RELEASE
    )

    # if we request all, all are ok
    assert is_config_selected_single_config_generator(
        current_config=BuildConfig.DEBUG, requested_config=BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID
    )
    assert is_config_selected_single_config_generator(
        current_config=BuildConfig.RELEASE, requested_config=BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID
    )
    assert is_config_selected_single_config_generator(
        current_config=BuildConfig.PARANOID, requested_config=BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID
    )
    assert is_config_selected_single_config_generator(
        current_config=BuildConfig.RELWITHDEBINFO, requested_config=BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID
    )
    assert not is_config_selected_single_config_generator(
        current_config=BuildConfig.DEBUG_RELEASE, requested_config=BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID
    )
    assert not is_config_selected_single_config_generator(
        current_config=BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID,
        requested_config=BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID,
    )

    assert not is_config_selected_single_config_generator(current_config="INVALID", requested_config=BuildConfig.DEBUG)  # type: ignore
    assert not is_config_selected_single_config_generator(current_config=BuildConfig.DEBUG, requested_config="INVALID")  # type: ignore
    assert not is_config_selected_single_config_generator(current_config="INVALID", requested_config="INVALID")  # type: ignore


def test_get_all_supported_workflow_descriptions() -> None:
    assert len(get_all_supported_workflow_descriptions(BuildConfig.DEBUG)) > 0
    assert len(get_all_supported_workflow_descriptions(BuildConfig.RELEASE)) > 0
    assert len(get_all_supported_workflow_descriptions(BuildConfig.RELWITHDEBINFO)) > 0
    assert len(get_all_supported_workflow_descriptions(BuildConfig.PARANOID)) > 0
    assert len(get_all_supported_workflow_descriptions(BuildConfig.DEBUG_RELEASE)) > 0
    assert len(get_all_supported_workflow_descriptions(BuildConfig.DEBUG_RELEASE_RELWITHDEBINFO_PARANOID)) > 0


def test_workflow_name_from_description() -> None:
    list = get_all_supported_workflow_descriptions(BuildConfig.DEBUG)
    for desc in list:
        name = workflow_name_from_description(desc)
        assert name.startswith("workflow-")
        assert name.endswith("-debug")


def test_get_supported_os_version_list() -> None:
    linux_versions = get_supported_os_version_list(OS.LINUX)
    assert len(linux_versions) > 0
    assert "ubuntu24.04" in linux_versions

    windows_versions = get_supported_os_version_list(OS.WINDOWS)
    assert len(windows_versions) > 0
    assert "v10" in windows_versions
    assert "v11" in windows_versions

    macos_versions = get_supported_os_version_list(OS.MACOS)
    assert len(macos_versions) == 0  # TODO add macos support

    invalid_versions = get_supported_os_version_list("INVALID")  # type: ignore
    assert len(invalid_versions) == 0
