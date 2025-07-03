from enum import StrEnum


class ExtractorTypes(StrEnum):
    """Enum describing the type of information source."""

    FILE = "file"
    CONFLUENCE = "confluence"
    SITEMAP = "sitemap"
    NONE = "None"
