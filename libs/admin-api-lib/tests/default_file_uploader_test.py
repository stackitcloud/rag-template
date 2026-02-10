import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from fastapi import UploadFile

from admin_api_lib.impl.api_endpoints.default_file_uploader import DefaultFileUploader
from admin_api_lib.models.status import Status
from admin_api_lib.utils.utils import sanitize_document_name


@pytest.fixture
def mocks():
    extractor_api = MagicMock()
    key_value_store = MagicMock()
    key_value_store.get_all.return_value = []
    key_value_store.start_run.return_value = "run-1"
    key_value_store.finish_run.return_value = None
    key_value_store.cancel_run.return_value = None
    key_value_store.is_cancelled_or_stale.return_value = False
    information_enhancer = MagicMock()
    information_enhancer.ainvoke = AsyncMock()
    chunker = MagicMock()
    document_deleter = MagicMock()
    document_deleter.adelete_document = AsyncMock()
    rag_api = MagicMock()
    information_mapper = MagicMock()
    return extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper


@pytest.mark.asyncio
async def test_handle_file_upload_success(mocks):
    extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper = mocks
    # setup mocks
    dummy_piece = MagicMock()
    extractor_api.extract_from_file_post.return_value = [dummy_piece]
    dummy_doc = MagicMock()
    information_mapper.extractor_information_piece2document.return_value = dummy_doc
    chunker.chunk.return_value = [dummy_doc]
    information_enhancer.ainvoke.return_value = [dummy_doc]
    dummy_rag = {"foo": "bar"}
    information_mapper.document2rag_information_piece.return_value = dummy_rag

    uploader = DefaultFileUploader(
        extractor_api,
        key_value_store,
        information_enhancer,
        chunker,
        document_deleter,
        rag_api,
        information_mapper,
        file_service=MagicMock(),
    )

    upload_filename = "file:doc1"

    await uploader._handle_source_upload("s3path", upload_filename, "doc1.txt", "http://base")

    key_value_store.upsert.assert_any_call(upload_filename, Status.READY)
    rag_api.upload_information_piece.assert_called_once_with([dummy_rag])
    document_deleter.adelete_document.assert_awaited_once_with(
        upload_filename,
        remove_from_key_value_store=False,
        remove_from_storage=False,
    )


@pytest.mark.asyncio
async def test_handle_file_upload_no_info_pieces(mocks):
    extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper = mocks
    extractor_api.extract_from_file_post.return_value = []

    uploader = DefaultFileUploader(
        extractor_api,
        key_value_store,
        information_enhancer,
        chunker,
        document_deleter,
        rag_api,
        information_mapper,
        file_service=MagicMock(),
    )
    filename = "file:doc2"
    await uploader._handle_source_upload("s3path", filename, "doc2.txt", "http://base")

    key_value_store.upsert.assert_any_call(filename, Status.ERROR)
    information_mapper.extractor_information_piece2document.assert_not_called()
    rag_api.upload_information_piece.assert_not_called()


@pytest.mark.asyncio
async def test_upload_file_already_processing_raises_error(mocks):
    extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper = mocks
    base_url = "http://base"
    file = MagicMock(spec=UploadFile)
    file.filename = "doc3.txt"
    file.read = AsyncMock(return_value=b"")
    source_name = f"file:{sanitize_document_name(file.filename)}"
    key_value_store.get_all.return_value = [(source_name, Status.PROCESSING)]

    uploader = DefaultFileUploader(
        extractor_api,
        key_value_store,
        information_enhancer,
        chunker,
        document_deleter,
        rag_api,
        information_mapper,
        file_service=MagicMock(),
    )

    with pytest.raises(HTTPException):
        await uploader.upload_file(base_url, file)
    key_value_store.upsert.assert_any_call(source_name, Status.ERROR)


@pytest.mark.asyncio
async def test_upload_file_starts_background_task(mocks):
    extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper = mocks
    base_url = "http://base"
    file = MagicMock(spec=UploadFile)
    file.filename = "doc4.txt"
    file.read = AsyncMock(return_value=b"content")
    key_value_store.get_all.return_value = []
    source_name = f"file:{sanitize_document_name(file.filename)}"

    uploader = DefaultFileUploader(
        extractor_api,
        key_value_store,
        information_enhancer,
        chunker,
        document_deleter,
        rag_api,
        information_mapper,
        file_service=MagicMock(),
    )

    # Verify no background tasks initially
    assert len(uploader._background_tasks) == 0

    await uploader.upload_file(base_url, file)

    # Verify processing status was set and background task was created
    key_value_store.upsert.assert_any_call(source_name, Status.PROCESSING)
    assert len(uploader._background_tasks) == 1
    assert uploader._background_tasks[0].get_name()  # Task was created


@pytest.mark.asyncio
async def test_handle_file_upload_cancelled_skips_terminal_status(mocks):
    extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper = mocks
    # setup mocks for a successful path
    dummy_piece = MagicMock()
    extractor_api.extract_from_file_post.return_value = [dummy_piece]
    dummy_doc = MagicMock()
    information_mapper.extractor_information_piece2document.return_value = dummy_doc
    chunker.chunk.return_value = [dummy_doc]
    information_enhancer.ainvoke.return_value = [dummy_doc]
    information_mapper.document2rag_information_piece.return_value = {"foo": "bar"}

    uploader = DefaultFileUploader(
        extractor_api,
        key_value_store,
        information_enhancer,
        chunker,
        document_deleter,
        rag_api,
        information_mapper,
        file_service=MagicMock(),
    )

    upload_filename = "file:cancelled-doc"
    key_value_store.start_run.return_value = "run-cancelled"
    key_value_store.is_cancelled_or_stale.return_value = True

    await uploader._handle_source_upload(
        "s3path",
        upload_filename,
        "doc.txt",
        "http://base",
        run_id="run-cancelled",
    )

    status_updates = [call.args for call in key_value_store.upsert.call_args_list]
    assert (upload_filename, Status.READY) not in status_updates
    assert (upload_filename, Status.ERROR) not in status_updates
    rag_api.upload_information_piece.assert_not_called()
