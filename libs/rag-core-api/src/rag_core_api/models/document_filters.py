from __future__ import annotations

import json
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel


class DocumentFilters(BaseModel):
    """DocumentFilters used to pre-filter retrieval by filenames/groups.

    - bebauungsplan: list of filenames to include (Bebauungsplan and Festsetzungen)
    - lbo: list of filenames to include (Landesbauordnung)
    """

    bebauungsplan: Optional[List[str]] = None
    lbo: Optional[List[str]] = None

    __properties: ClassVar[List[str]] = ["bebauungsplan", "lbo"]

    def to_json(self) -> str:
        return self.model_dump_json(by_alias=True, exclude_unset=True)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)

    @classmethod
    def from_json(cls, json_str: str) -> "DocumentFilters":
        return cls.model_validate_json(json_str)

    @classmethod
    def from_dict(cls, obj: Dict[str, Any] | None) -> "DocumentFilters | None":
        if obj is None:
            return None
        return cls.model_validate(obj)
