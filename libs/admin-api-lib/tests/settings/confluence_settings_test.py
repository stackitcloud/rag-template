import pytest
from admin_api_lib.impl.settings.confluence_settings import ConfluenceSettings
from admin_api_lib.impl.utils.comma_separated_str_list import CommaSeparatedStrList
from admin_api_lib.impl.utils.comma_separated_bool_list import CommaSeparatedBoolList


def test_default_values():
    # When no settings are provided, all lists default to empty lists.
    settings = ConfluenceSettings()
    assert settings.url == CommaSeparatedStrList()
    assert settings.token == CommaSeparatedStrList()
    assert settings.space_key == CommaSeparatedStrList()
    assert settings.document_name == CommaSeparatedStrList()
    # Bool lists are empty by default if no url is provided.
    assert settings.verify_ssl == CommaSeparatedBoolList()
    assert settings.include_attachments == CommaSeparatedBoolList()
    assert settings.keep_markdown_format == CommaSeparatedBoolList()
    assert settings.keep_newlines == CommaSeparatedBoolList()


def test_valid_initialization_matching_lengths():
    # Provide all settings with matching lengths.
    urls = "http://confluence1, http://confluence2"
    tokens = "token1, token2"
    space_keys = "SPACE1, SPACE2"
    document_names = "Doc1, Doc2"
    verify_ssl = "True, False"
    include_attachments = "False, True"
    keep_markdown_format = "True, True"
    keep_newlines = "False, False"

    settings = ConfluenceSettings(
        url=urls,
        token=tokens,
        space_key=space_keys,
        document_name=document_names,
        verify_ssl=verify_ssl,
        include_attachments=include_attachments,
        keep_markdown_format=keep_markdown_format,
        keep_newlines=keep_newlines,
    )

    # Verify that the comma separated lists have been properly parsed.
    assert settings.url == CommaSeparatedStrList(["http://confluence1", "http://confluence2"])
    assert settings.token == CommaSeparatedStrList(["token1", "token2"])
    assert settings.space_key == CommaSeparatedStrList(["SPACE1", "SPACE2"])
    assert settings.document_name == CommaSeparatedStrList(["Doc1", "Doc2"])
    assert settings.verify_ssl == CommaSeparatedBoolList([True, False])
    assert settings.include_attachments == CommaSeparatedBoolList([False, True])
    assert settings.keep_markdown_format == CommaSeparatedBoolList([True, True])
    assert settings.keep_newlines == CommaSeparatedBoolList([False, False])


def test_mismatched_list_lengths():
    # Provide mismatched lengths for comma separated fields, should raise ValueError.
    urls = "http://confluence1, http://confluence2, http://confluence3"
    tokens = "token1, token2"  # shorter than url list
    with pytest.raises(ValueError):
        ConfluenceSettings(
            url=urls,
            token=tokens,
            space_key="SPACE1, SPACE2, SPACE3",
            document_name="Doc1, Doc2, Doc3",
        )


def test_default_bool_values_when_missing():
    # Provide only url and leave bool fields empty to see if they are set to defaults.
    urls = "http://confluence1, http://confluence2, http://confluence3"
    settings = ConfluenceSettings(
        url=urls,
        token="token1, token2, token3",
        space_key="SPACE1, SPACE2, SPACE3",
        document_name="Doc1, Doc2, Doc3",
    )
    # Defaults for bool fields: verify_ssl True, include_attachments False,
    # keep_markdown_format True, keep_newlines True, for each entry.
    expected_verify_ssl = CommaSeparatedBoolList([True, True, True])
    expected_include_attachments = CommaSeparatedBoolList([False, False, False])
    expected_keep_markdown_format = CommaSeparatedBoolList([True, True, True])
    expected_keep_newlines = CommaSeparatedBoolList([True, True, True])
    assert settings.verify_ssl == expected_verify_ssl
    assert settings.include_attachments == expected_include_attachments
    assert settings.keep_markdown_format == expected_keep_markdown_format
    assert settings.keep_newlines == expected_keep_newlines


def test_bool_fields_not_overwritten_when_provided():
    # Provide bool fields explicitly; they should not be overwritten by defaults.
    urls = "http://confluence1, http://confluence2"
    settings = ConfluenceSettings(
        url=urls,
        token="token1, token2",
        space_key="SPACE1, SPACE2",
        document_name="Doc1, Doc2",
        verify_ssl="False, False",
        include_attachments="True, True",
        keep_markdown_format="False, False",
        keep_newlines="False, True",
    )
    expected_verify_ssl = CommaSeparatedBoolList([False, False])
    expected_include_attachments = CommaSeparatedBoolList([True, True])
    expected_keep_markdown_format = CommaSeparatedBoolList([False, False])
    expected_keep_newlines = CommaSeparatedBoolList([False, True])
    assert settings.verify_ssl == expected_verify_ssl
    assert settings.include_attachments == expected_include_attachments
    assert settings.keep_markdown_format == expected_keep_markdown_format
    assert settings.keep_newlines == expected_keep_newlines
