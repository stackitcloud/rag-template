import pytest
from admin_api_lib.impl.utils.comma_separated_bool_list import CommaSeparatedBoolList


def test_validate_empty_string():
    # An empty string should return an empty list.
    assert CommaSeparatedBoolList.validate("", None) == []


def test_validate_string_input():
    # Test a typical comma separated string.
    # "true", "yes", and "1" are considered True, all others are False.
    input_str = "true, false, yes, no, 1, 0,  ,TRUE, YeS"
    expected = [
        True,  # "true"
        False,  # "false"
        True,  # "yes"
        False,  # "no"
        True,  # "1"
        False,  # "0"
        True,  # "TRUE"
        True,  # "YeS"
    ]
    # Note: extra whitespace items are ignored.
    result = CommaSeparatedBoolList.validate(input_str, None)
    assert result == expected


def test_validate_string_with_extra_commas():
    # Test string with extra commas and spaces.
    input_str = "true,, yes, ,false"
    expected = [True, True, False]
    result = CommaSeparatedBoolList.validate(input_str, None)
    assert result == expected


def test_validate_list_input():
    # When input is a list, each element is cast to bool.
    input_list = [0, 1, True, False, "non-empty", ""]
    expected = [
        False,  # bool(0)
        True,  # bool(1)
        True,  # bool(True)
        False,  # bool(False)
        True,  # bool("non-empty")
        False,  # bool("")
    ]
    result = CommaSeparatedBoolList.validate(input_list, None)
    assert result == expected


def test_invalid_input_type():
    # Passing a non-string and non-list should raise a ValueError.
    with pytest.raises(ValueError):
        CommaSeparatedBoolList.validate(123, None)
