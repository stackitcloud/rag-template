"""Utility module to handle comma separated string input that represents boolean values."""

from typing import Any


class CommaSeparatedBoolList(list):
    """
    A subclass of list that converts comma-separated strings or lists into a list of booleans.

    Notes
    -----
    - For string inputs, splits the string by commas and converts recognized true values ("true", "1", "yes") to True.
    - An empty or whitespace-only string returns an empty list.
    - For list inputs, each element is converted to a boolean.
    """

    @classmethod
    def validate(cls, v: Any, info) -> list[bool]:
        """
        Validate and convert the input into a list of booleans.

        Parameters
        ----------
        v : Any
            Input value, either a comma separated string or a list.
        info : Any
            Additional context information (unused).

        Returns
        -------
        list of bool
            List of booleans parsed from the input. An empty string returns an empty list.

        Raises
        ------
        ValueError
            If v is not a string or list.
        """

        def str_to_bool(s: str) -> bool:
            return s.lower() in ("true", "1", "yes")

        if isinstance(v, str):
            if v.strip() == "":
                return []
            return [str_to_bool(item.strip()) for item in v.split(",") if item.strip()]
        elif isinstance(v, list):
            return [bool(item) for item in v]
        raise ValueError("Not a valid comma separated boolean list")

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
