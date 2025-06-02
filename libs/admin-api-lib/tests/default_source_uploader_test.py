# ignore:

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from admin_api_lib.impl.api_endpoints.default_source_uploader import DefaultSourceUploader
from admin_api_lib.models.status import Status
from admin_api_lib.utils.utils import sanitize_document_name
from admin_api_lib.impl.api_endpoints import default_source_uploader


@pytest.fixture
def mocks():
    extractor_api = MagicMock()
    key_value_store = MagicMock()
    key_value_store.get_all.return_value = []
    information_enhancer = MagicMock()
    information_enhancer.ainvoke = AsyncMock()
    chunker = MagicMock()
    document_deleter = MagicMock()
    document_deleter.adelete_document = AsyncMock()
    rag_api = MagicMock()
    information_mapper = MagicMock()
    return extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper


@pytest.mark.asyncio
async def test_handle_source_upload_success(mocks):
    extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper = mocks
    # Setup mocks
    dummy_piece = MagicMock()
    extractor_api.extract_from_source.return_value = [dummy_piece]
    dummy_doc = MagicMock()
    information_mapper.extractor_information_piece2document.return_value = dummy_doc
    chunker.chunk.return_value = [dummy_doc]
    information_enhancer.ainvoke.return_value = [dummy_doc]
    dummy_rag_piece = {"p": "v"}
    information_mapper.document2rag_information_piece.return_value = dummy_rag_piece

    uploader = DefaultSourceUploader(
        extractor_api,
        key_value_store,
        information_enhancer,
        chunker,
        document_deleter,
        rag_api,
        information_mapper,
    )

    await uploader._handle_source_upload("source1", "type1", [])

    key_value_store.upsert.assert_any_call("source1", Status.READY)
    rag_api.upload_information_piece.assert_called_once_with([dummy_rag_piece])
    document_deleter.adelete_document.assert_awaited_once_with("source1", remove_from_key_value_store=False)


@pytest.mark.asyncio
async def test_handle_source_upload_no_info_pieces(mocks):
    extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper = mocks
    extractor_api.extract_from_source.return_value = []

    uploader = DefaultSourceUploader(
        extractor_api,
        key_value_store,
        information_enhancer,
        chunker,
        document_deleter,
        rag_api,
        information_mapper,
    )
    await uploader._handle_source_upload("source2", "type2", [])

    key_value_store.upsert.assert_any_call("source2", Status.ERROR)
    information_mapper.extractor_information_piece2document.assert_not_called()
    rag_api.upload_information_piece.assert_not_called()


@pytest.mark.asyncio
async def test_upload_source_already_processing_raises_error(mocks):
    extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper = mocks
    source_type = "typeX"
    name = "Doc Name"
    source_name = f"{source_type}:{sanitize_document_name(name)}"
    key_value_store.get_all.return_value = [(source_name, Status.PROCESSING)]
    uploader = DefaultSourceUploader(
        extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper
    )
    with pytest.raises(HTTPException):
        # use default timeout
        await uploader.upload_source(source_type, name, [])
    key_value_store.upsert.assert_any_call(source_name, Status.ERROR)


@pytest.mark.asyncio
async def test_upload_source_no_timeout(mocks, monkeypatch):
    extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper = mocks
    key_value_store.get_all.return_value = []
    source_type = "typeZ"
    name = "quick"
    # patch Thread so no actual background work is done
    dummy_thread = MagicMock()
    monkeypatch.setattr(default_source_uploader, "Thread", lambda *args, **kwargs: dummy_thread)
    uploader = DefaultSourceUploader(
        extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper
    )
    # should not raise
    await uploader.upload_source(source_type, name, [], timeout=1.0)
    # only PROCESSING status upserted, no ERROR
    assert any(call.args[1] == Status.PROCESSING for call in key_value_store.upsert.call_args_list)
    assert not any(call.args[1] == Status.ERROR for call in key_value_store.upsert.call_args_list)
    dummy_thread.start.assert_called_once()


@pytest.mark.asyncio
async def test_upload_source_timeout_error(mocks, monkeypatch):
    extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper = mocks
    key_value_store.get_all.return_value = []
    source_type = "typeTimeout"
    name = "slow"
    source_name = f"{source_type}:{sanitize_document_name(name)}"

    # monkey-patch the handler to sleep so that timeout triggers
    async def fake_handle(self, source_name_arg, source_type_arg, kwargs_arg):
        await asyncio.sleep(3600)

    # patch handler and Thread to trigger timeout synchronously
    monkeypatch.setattr(default_source_uploader.DefaultSourceUploader, "_handle_source_upload", fake_handle)

    def FakeThread(target, args=(), **kwargs):
        # this ensures serial execution, so that the error status can be checked
        class T:
            def start(self):
                target(*args)

            def is_alive(self):
                return False

        return T()

    monkeypatch.setattr(default_source_uploader, "Thread", FakeThread)
    uploader = DefaultSourceUploader(
        extractor_api, key_value_store, information_enhancer, chunker, document_deleter, rag_api, information_mapper
    )
    # no exception should be raised; timeout path sets ERROR status

    await uploader.upload_source(source_type, name, [], timeout=1.0)
    # first call marks PROCESSING, second marks ERROR
    calls = [call.args for call in key_value_store.upsert.call_args_list]
    assert (source_name, Status.PROCESSING) in calls
    assert (source_name, Status.ERROR) in calls
