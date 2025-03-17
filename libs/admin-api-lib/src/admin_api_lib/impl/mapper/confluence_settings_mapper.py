"""Module for the ConfluenceSettingsMapper class."""

from admin_api_lib.extractor_api_client.openapi_client.models.confluence_parameters import (
    ConfluenceParameters,
)
from admin_api_lib.impl.settings.confluence_settings import ConfluenceSettings


class ConfluenceSettingsMapper:
    """Mapper class for converting ConfluenceSettings to ConfluenceParameters."""

    @staticmethod
    def map_settings_to_params(settings: ConfluenceSettings, index) -> ConfluenceParameters:
        """
        Map ConfluenceSettings to ConfluenceParameters.

        Parameters
        ----------
        settings : ConfluenceSettings
            The settings object containing Confluence configuration.

        Returns
        -------
        ConfluenceParameters
            The parameters object for API consumption.
        """
        return ConfluenceParameters(
            url=settings.url[index],
            token=settings.token[index],
            space_key=settings.space_key[index],
            include_attachments=settings.include_attachments[index],
            keep_markdown_format=settings.keep_markdown_format[index],
            keep_newlines=settings.keep_newlines[index],
            document_name=settings.document_name[index],
            confluence_kwargs=[{"key": "verify_ssl", "value": settings.verify_ssl[index]}],
        )
