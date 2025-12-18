"""Unit tests for sitemap HTML parsing utilities.

These tests validate that the sitemap extractor helper functions correctly:

- extract human-readable content from common documentation site layouts
- derive basic metadata such as title and source URL

Notes
-----
The underlying implementation uses BeautifulSoup. If the optional dependency isn't
installed, these tests are skipped.
"""

import pytest

from extractor_api_lib.impl.utils.sitemap_extractor_utils import (
    astro_sitemap_metadata_parser_function,
    astro_sitemap_parser_function,
    docusaurus_sitemap_metadata_parser_function,
    docusaurus_sitemap_parser_function,
    generic_sitemap_metadata_parser_function,
)


pytest.importorskip("bs4")


def test_docusaurus_parser_extracts_main_article_text():
    """Ensure the Docusaurus parser extracts main article content and drops navigation."""
    html = """
    <html>
      <body>
        <nav>Navigation</nav>
        <main>
          <article>
            <h1>Doc Title</h1>
            <p>Doc content paragraph.</p>
          </article>
        </main>
      </body>
    </html>
    """

    text = docusaurus_sitemap_parser_function(html)

    assert "Navigation" not in text
    assert "Doc Title" in text
    assert "Doc content paragraph." in text


def test_docusaurus_meta_parser_sets_title_and_source():
    """Ensure the Docusaurus metadata parser sets title from H1 and includes the source URL."""
    html = """
    <html>
      <head><title>Ignored title</title></head>
      <body>
        <main>
          <article><h1>Doc Title</h1><p>Content</p></article>
        </main>
      </body>
    </html>
    """

    parsed = docusaurus_sitemap_metadata_parser_function({"loc": "https://example.com/page"}, html)

    assert parsed["source"] == "https://example.com/page"
    assert parsed["title"] == "Doc Title"


def test_astro_parser_prefers_starlight_article():
    """Ensure the Astro parser prefers Starlight content and drops irrelevant elements."""
    html = """
    <html>
      <body>
        <aside>Sidebar</aside>
        <main data-pagefind-body>
          <div class="markdown-header-container"><h1>Astro Title</h1></div>
          <div class="sl-markdown-content">
            <p>Astro content.</p>
          </div>
        </main>
      </body>
    </html>
    """

    text = astro_sitemap_parser_function(html)

    assert "Sidebar" not in text
    assert "Astro content." in text


def test_astro_meta_parser_sets_title_and_source():
    """Ensure the Astro metadata parser extracts title from the header container and source URL."""
    html = """
    <html>
      <head><title>Fallback title</title></head>
      <body>
        <main data-pagefind-body>
          <div class="markdown-header-container"><h1>Astro Title</h1></div>
          <div class="sl-markdown-content"><p>Content</p></div>
        </main>
      </body>
    </html>
    """

    parsed = astro_sitemap_metadata_parser_function({"loc": "https://example.com/astro"}, html)

    assert parsed["source"] == "https://example.com/astro"
    assert parsed["title"] == "Astro Title"


def test_meta_parser_falls_back_to_title_tag():
    """Ensure the generic metadata parser falls back to the <title> tag when no H1 exists."""
    html = """
    <html>
      <head><title>Title Tag</title></head>
      <body>
        <main><article><p>No h1 here.</p></article></main>
      </body>
    </html>
    """

    parsed = generic_sitemap_metadata_parser_function({"loc": "https://example.com/no-h1"}, html)

    assert parsed["title"] == "Title Tag"
