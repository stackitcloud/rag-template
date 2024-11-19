"""Contains settings regarding the chunker."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ConfluenceSettings(BaseSettings):
    """Contains settings regarding the chunker.

    Attributes:
        url (Optional[str]): The Confluence URL.
        token (Optional[str]): The authentication token.
        space_key (Optional[str]): The Confluence space key.
        include_attachments (bool): Whether to include attachments.
        keep_markdown_format (bool): Whether to keep markdown formatting.
        keep_newlines (bool): Whether to keep newlines.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "CONFLUENCE_"
        case_sensitive = False

    url: str | None = Field(default=None)
    token: str | None = Field(default=None)
    space_key: str | None = Field(default=None)
    include_attachments: bool = Field(default=False)
    keep_markdown_format: bool = Field(default=True)
    keep_newlines: bool = Field(default=True)
