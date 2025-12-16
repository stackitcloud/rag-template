"""Language detection chain.

# Assumptions:
# - We want a robust return of a 2-letter ISO 639-1 language code (lowercase),
#   defaulting to "en" when unsure or parsing fails.
# - We instruct the LLM to produce structured JSON and include format instructions,
#   but we still parse defensively to handle non-conforming outputs.
"""

import json
import re
from typing import Any, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, field_validator
from langchain_core.output_parsers import PydanticOutputParser

from rag_core_api.impl.graph.graph_state.graph_state import AnswerGraphState
from rag_core_lib.runnables.async_runnable import AsyncRunnable
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager
from rag_core_api.utils.utils import (
    strip_code_fences,
    norm_lang,
    extract_lang_from_parsed,
    JSONISH_DQ_RE,
    JSONISH_SQ_RE,
    JSONISH_LOOSE_RE,
)


RunnableInput = AnswerGraphState
RunnableOutput = str


class LanguageDetectionChain(AsyncRunnable[RunnableInput, RunnableOutput]):
    """Base class for language detection of the input question."""

    def __init__(self, langfuse_manager: LangfuseManager):
        """Initialize LanguageDetectionChain with LangfuseManager."""
        self._langfuse_manager = langfuse_manager

    @staticmethod
    def _strict_json_parse(text: str) -> Optional[str]:
        """Attempt to strictly parse JSON and extract the language code."""
        try:
            data = json.loads(text)
            c = extract_lang_from_parsed(data)
            if c:
                return c
        except (json.JSONDecodeError, TypeError, ValueError):
            return None

    @staticmethod
    def _loose_json_parse(text: str) -> Optional[str]:
        for pattern in (JSONISH_DQ_RE, JSONISH_SQ_RE, JSONISH_LOOSE_RE):
            m = pattern.search(text)
            if m:
                c = norm_lang(m.group(1))
                if c:
                    return c
        return None

    @staticmethod
    def _extract_language_code(raw_output: Any) -> str:
        """Extract a two-letter ISO 639-1 language code; default to 'en' on failure."""
        # 1) Already parsed structures
        c = extract_lang_from_parsed(raw_output)
        if c:
            return c

        # 2) Strings (common case)
        if isinstance(raw_output, str):
            text = raw_output.strip().lstrip("\ufeff")
            text = strip_code_fences(text)

            # a) Direct 'xx' or 'xx-YY'
            c = norm_lang(text)
            if c:
                return c

            # b) Try strict JSON parsing
            c = LanguageDetectionChain._strict_json_parse(text)
            if c:
                return c

            # c) JSON-ish fallbacks (handles single quotes, loose key/value, etc.)
            c = LanguageDetectionChain._loose_json_parse(text)
            if c:
                return c

        # Fallback
        return "en"

    async def ainvoke(
        self, chain_input: RunnableInput, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> RunnableOutput:
        """
        Asynchronously detects the language and returns an ISO 639-1 code.

        Returns
        -------
        RunnableOutput
            Two-letter ISO 639-1 language code in lowercase (e.g., "en", "de").
        """
        raw = await self._create_chain().ainvoke(chain_input, config=config)
        return self._extract_language_code(raw)

    def _create_chain(self) -> Runnable:
        # Provide format instructions to the prompt using a minimal Pydantic schema.
        class _LangSchema(BaseModel):
            language: str

            @field_validator("language")
            @classmethod
            def two_letter_lower(cls, v: str) -> str:
                v = v.strip().lower()
                if not re.fullmatch(r"[a-z]{2}", v):
                    raise ValueError("language must be a two-letter ISO 639-1 code")
                return v

        # We don't use PydanticOutputParser directly in the chain to avoid hard failures
        # when the model doesn't follow instructions. Instead, we keep a string parser and
        # parse defensively in ainvoke(). We still inject format instructions to guide the LLM.
        try:
            fmt_instructions = PydanticOutputParser(pydantic_object=_LangSchema).get_format_instructions()
        except Exception:
            fmt_instructions = (
                "Return a strict JSON object with a single field 'language' as a "
                'lowercase two-letter ISO 639-1 code, e.g. {"language":"de"}.'
            )

        prompt = self._langfuse_manager.get_base_prompt(self.__class__.__name__).partial(
            format_instructions=fmt_instructions
        )

        return prompt | self._langfuse_manager.get_base_llm(self.__class__.__name__) | StrOutputParser()
