from pydantic import BaseModel, StrictStr
from typing import Optional


class SearchRequest(BaseModel):
    """
    Represents a search request.

    Attributes:
        search_term (str): The search term to be used.
        metadata (Optional[dict[str, str]]): Additional metadata for the search request.
    """

    search_term: StrictStr
    metadata: Optional[dict[str, str]] = None
