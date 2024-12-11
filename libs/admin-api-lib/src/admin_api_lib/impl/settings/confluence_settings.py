"""Contains settings regarding the confluence."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ConfluenceSettings(BaseSettings):
    """Contains settings regarding confluence.

    Attributes
    ----------
    url (Optional[str]): The Confluence URL.
    token (Optional[str]): The authentication token.
    space_key (Optional[str]): The Confluence space key.
    include_attachments (bool): Whether to include attachments.
    keep_markdown_format (bool): Whether to keep markdown formatting.
    keep_newlines (bool): Whether to keep newlines.
    document_name (Optional[str]): The name of the document. Should be a name like "stackit-confluence".
        This name will be shown in the admin-frontend and will be used to identify the document in the RAG backend.
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
    document_name: str | None = Field(default=None)
