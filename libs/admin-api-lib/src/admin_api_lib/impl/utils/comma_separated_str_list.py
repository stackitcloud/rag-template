"""
Comma Separated String List Utility Module.

This module provides a custom list type to validate and convert inputs into
a list of strings. It splits comma separated strings and converts list elements
to strings.

Raises
------
ValueError
    If the provided input is neither a string nor a list.
"""

from typing import Any


class CommaSeparatedStrList(list):
    """
    Custom list type that validates comma separated strings.

    - If input is a string: splits by commas and strips whitespace.
    - If input is a list: converts all elements to strings.

    Raises
    ------
    ValueError
        For invalid input type.
    """

    @classmethod
    def validate(cls, v: Any, info) -> list[str]:
        """
        Convert input to a validated list of strings.

        Parameters
        ----------
        v : Any
            A comma-separated string or a list containing items to be converted.
        info : Any
            Additional contextual information (not used in current implementation).

        Returns
        -------
        list of str
            A list of trimmed strings. Returns an empty list for an empty or whitespace-only string.

        Raises
        ------
        ValueError
            If the input v is neither a string nor a list.
        """
        if isinstance(v, str):
            if v.strip() == "":
                return []
            return [item.strip() for item in v.split(",") if item.strip()]
        elif isinstance(v, list):
            return [str(item) for item in v]
        raise ValueError("Not a valid comma separated string list")

    @classmethod
    def __get_validators__(cls):
        """
        Get validator functions for Pydantic to use with this data type.

        This method is called by Pydantic during model initialization to collect
        validator functions for fields using this custom data type.

        Returns
        -------
        generator
            A generator yielding validator functions, specifically `cls.validate`,
            which will be applied to validate and convert input values.
        """
        yield cls.validate
