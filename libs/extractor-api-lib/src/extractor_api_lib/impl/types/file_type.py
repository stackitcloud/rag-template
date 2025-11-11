"""Module containing the FileType enum."""

from enum import StrEnum


class FileType(StrEnum):
    """Enum describing the type of file being processed."""

    NONE = "None"
    PDF = "PDF"
    DOCX = "DOCX"
    PPTX = "PPTX"
    XML = "XML"
    EPUB = "EPUB"
