import pytest
from admin_api_lib.impl.utils.comma_separated_str_list import CommaSeparatedStrList


def test_validate_string():
    # simple comma separated string
    input_str = "a, b, c"
    expected = ["a", "b", "c"]
    result = CommaSeparatedStrList.validate(input_str, None)
    assert result == expected

    input_str = "a"
    expected = ["a"]
    result = CommaSeparatedStrList.validate(input_str, None)
    assert result == expected


def test_validate_string_with_extra_spaces():
    # string with extra spaces and empty items
    input_str = " apple ,  banana , , cherry , "
    expected = ["apple", "banana", "cherry"]
    result = CommaSeparatedStrList.validate(input_str, None)
    assert result == expected


def test_validate_empty_string():
    input_str = ""
    expected = []
    result = CommaSeparatedStrList.validate(input_str, None)
    assert result == expected


def test_validate_string_only_spaces():
    input_str = "   "
    expected = []
    result = CommaSeparatedStrList.validate(input_str, None)
    assert result == expected


def test_validate_list():
    input_list = [1, "2", 3.0, " test "]
    expected = ["1", "2", "3.0", " test "]
    result = CommaSeparatedStrList.validate(input_list, None)
    assert result == expected


def test_invalid_input_type():
    with pytest.raises(ValueError):
        CommaSeparatedStrList.validate(12345, None)
