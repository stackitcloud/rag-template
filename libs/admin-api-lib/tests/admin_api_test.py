import pytest
from unittest.mock import AsyncMock, MagicMock

from admin_api_lib.impl.admin_api import AdminApi


@pytest.mark.asyncio
async def test_delete_document_requests_cancellation_before_delete():
    admin_api = AdminApi()
    document_deleter = MagicMock()
    document_deleter.adelete_document = AsyncMock()
    file_uploader = MagicMock()
    source_uploader = MagicMock()

    identification = "file:doc.pdf"
    await admin_api.delete_document(
        identification=identification,
        document_deleter=document_deleter,
        file_uploader=file_uploader,
        source_uploader=source_uploader,
    )

    file_uploader.cancel_upload.assert_called_once_with(identification)
    source_uploader.cancel_upload.assert_called_once_with(identification)
    document_deleter.adelete_document.assert_awaited_once_with(identification)
