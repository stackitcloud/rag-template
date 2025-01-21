"""Module for the SearchRequest data type."""

from pydantic import BaseModel, StrictStr
from typing import Optional


class SearchRequest(BaseModel):
    """
    Represents a search request.

    Parameters
    ----------
    search_term : str
        The search term to be used.
    metadata : Optional[dict[str, str]], optional
        Additional metadata for the search request (default None)
    """

    search_term: StrictStr
    metadata: Optional[dict[str, str]] = None
