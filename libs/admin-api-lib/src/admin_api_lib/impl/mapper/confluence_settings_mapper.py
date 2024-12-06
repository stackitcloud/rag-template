"""Module for the ConfluenceSettingsMapper class."""

from admin_api_lib.impl.settings.confluence_settings import ConfluenceSettings
from admin_api_lib.extractor_api_client.openapi_client.models.confluence_parameters import ConfluenceParameters


class ConfluenceSettingsMapper:
    """Mapper class for converting ConfluenceSettings to ConfluenceParameters."""

    @staticmethod
    def map_settings_to_params(settings: ConfluenceSettings) -> ConfluenceParameters:
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
            url=settings.url,
            token=settings.token,
            space_key=settings.space_key,
            include_attachments=settings.include_attachments,
            keep_markdown_format=settings.keep_markdown_format,
            keep_newlines=settings.keep_newlines,
        )
