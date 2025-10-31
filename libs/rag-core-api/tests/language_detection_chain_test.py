"""Unit tests for LanguageDetectionChain.

- Validates happy path with structured JSON output
- Validates fallback behavior on non-JSON outputs
"""

import pytest
from langchain_community.llms.fake import FakeListLLM
from unittest.mock import MagicMock

from rag_core_api.impl.answer_generation_chains.language_detection_chain import LanguageDetectionChain
from rag_core_api.impl.graph.graph_state.graph_state import AnswerGraphState
from rag_core_api.prompt_templates.language_detection_prompt import LANGUAGE_DETECTION_PROMPT
from mocks import MockLangfuseManager


@pytest.mark.asyncio
async def test_language_detection_returns_iso_code_json():
    """LLM returns strict JSON; chain extracts two-letter ISO code."""
    llm = FakeListLLM(responses=['{"language": "de"}'])
    mock_langfuse = MagicMock()
    manager = MockLangfuseManager(
        langfuse=mock_langfuse,
        managed_prompts={LanguageDetectionChain.__name__: LANGUAGE_DETECTION_PROMPT},
        llm=llm,
    )

    chain = LanguageDetectionChain(manager)
    state = AnswerGraphState.create(
        question="Was ist die Hauptstadt von Deutschland?",
        history="",
        error_messages=[],
        finish_reasons=[],
        information_pieces=[],
        langchain_documents=[],
    )

    result = await chain.ainvoke(state)
    assert result == "de"


@pytest.mark.asyncio
async def test_language_detection_fallback_to_en_on_garbage():
    """Non-JSON response triggers fallback to 'en'."""
    # LLM returns non-JSON, the chain should fall back to 'en'
    llm = FakeListLLM(responses=["I think it is German"])
    mock_langfuse = MagicMock()
    manager = MockLangfuseManager(
        langfuse=mock_langfuse,
        managed_prompts={LanguageDetectionChain.__name__: LANGUAGE_DETECTION_PROMPT},
        llm=llm,
    )

    chain = LanguageDetectionChain(manager)
    state = AnswerGraphState.create(
        question="Was ist die Hauptstadt von Deutschland?",
        history="",
        error_messages=[],
        finish_reasons=[],
        information_pieces=[],
        langchain_documents=[],
    )

    result = await chain.ainvoke(state)
    assert result == "en"


@pytest.mark.asyncio
async def test_language_detection_accepts_code_fenced_json():
    """Code-fenced JSON is parsed after stripping fences."""
    llm = FakeListLLM(responses=['```json\n{"language": "fr"}\n```'])
    mock_langfuse = MagicMock()
    manager = MockLangfuseManager(
        langfuse=mock_langfuse,
        managed_prompts={LanguageDetectionChain.__name__: LANGUAGE_DETECTION_PROMPT},
        llm=llm,
    )

    chain = LanguageDetectionChain(manager)
    state = AnswerGraphState.create(
        question="Quelle est la capitale de l'Allemagne ?",
        history="",
        error_messages=[],
        finish_reasons=[],
        information_pieces=[],
        langchain_documents=[],
    )

    result = await chain.ainvoke(state)
    assert result == "fr"


@pytest.mark.asyncio
async def test_language_detection_accepts_locale_variant_and_normalizes():
    """Locale variants like de-DE normalize to base code 'de'."""
    llm = FakeListLLM(responses=['{"language": "de-DE"}'])
    mock_langfuse = MagicMock()
    manager = MockLangfuseManager(
        langfuse=mock_langfuse,
        managed_prompts={LanguageDetectionChain.__name__: LANGUAGE_DETECTION_PROMPT},
        llm=llm,
    )

    chain = LanguageDetectionChain(manager)
    state = AnswerGraphState.create(
        question="Was ist die Hauptstadt von Deutschland?",
        history="",
        error_messages=[],
        finish_reasons=[],
        information_pieces=[],
        langchain_documents=[],
    )

    result = await chain.ainvoke(state)
    assert result == "de"


@pytest.mark.asyncio
async def test_language_detection_handles_single_quoted_jsonish():
    """Single-quoted JSON-ish text is handled via regex fallback."""
    llm = FakeListLLM(responses=["{'language': 'es'}"])
    mock_langfuse = MagicMock()
    manager = MockLangfuseManager(
        langfuse=mock_langfuse,
        managed_prompts={LanguageDetectionChain.__name__: LANGUAGE_DETECTION_PROMPT},
        llm=llm,
    )

    chain = LanguageDetectionChain(manager)
    state = AnswerGraphState.create(
        question="¿Cuál es la capital de Alemania?",
        history="",
        error_messages=[],
        finish_reasons=[],
        information_pieces=[],
        langchain_documents=[],
    )

    result = await chain.ainvoke(state)
    assert result == "es"


@pytest.mark.asyncio
async def test_language_detection_handles_loose_kv_format():
    """Loose key-value format like language: "it" is parsed."""
    llm = FakeListLLM(responses=['language: "it"'])
    mock_langfuse = MagicMock()
    manager = MockLangfuseManager(
        langfuse=mock_langfuse,
        managed_prompts={LanguageDetectionChain.__name__: LANGUAGE_DETECTION_PROMPT},
        llm=llm,
    )

    chain = LanguageDetectionChain(manager)
    state = AnswerGraphState.create(
        question="Qual è la capitale della Germania?",
        history="",
        error_messages=[],
        finish_reasons=[],
        information_pieces=[],
        langchain_documents=[],
    )

    result = await chain.ainvoke(state)
    assert result == "it"
