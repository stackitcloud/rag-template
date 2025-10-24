"""Tests for rag_core_api.utils.utils language parsing helpers."""

from rag_core_api.utils.utils import norm_lang, strip_code_fences, extract_lang_from_parsed


def test_norm_lang_variants():
    """Ensure various inputs normalize to ISO 639-1 codes or empty string."""
    assert norm_lang("de") == "de"
    assert norm_lang("DE") == "de"
    assert norm_lang("de-DE") == "de"
    assert norm_lang("en_US") == "en"
    assert norm_lang("xx-yy") == "xx"
    assert norm_lang("   fr  ") == "fr"
    assert norm_lang("not-a-code") == ""
    assert norm_lang(123) == ""


def test_strip_code_fences():
    """Strip code fences and return clean JSON text."""
    fenced = """```json\n{\n  \"language\": \"de\"\n}\n```"""
    assert strip_code_fences(fenced) == '{\n  "language": "de"\n}'


def test_extract_from_parsed():
    """Extract language from parsed structures like dicts and lists."""
    assert extract_lang_from_parsed({"language": "de"}) == "de"
    assert extract_lang_from_parsed([{"language": "en-US"}]) == "en"
    assert extract_lang_from_parsed({}) == ""
    assert extract_lang_from_parsed(None) == ""
