"""Module containing utility functions for sitemap extraction."""

from typing import Any, Union
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, Tag


def _as_soup(content: Union[str, BeautifulSoup]) -> BeautifulSoup:
    if isinstance(content, BeautifulSoup):
        return content
    return BeautifulSoup(content, "html.parser")


def _remove_non_content_elements(root: Tag) -> None:
    for selector in ("script", "style", "noscript", "nav", "aside", "footer", "form"):
        for element in root.find_all(selector):
            element.decompose()


def _extract_text(root: Tag) -> str:
    _remove_non_content_elements(root)
    return root.get_text(separator=" ", strip=True)


def _select_docusaurus_root(soup: BeautifulSoup) -> Tag:
    # Docusaurus v2 pages typically render the Markdown content inside <main><article>...</article></main>.
    root = soup.select_one("main article")
    if root is not None:
        return root
    root = soup.find("article")
    if root is not None:
        return root
    root = soup.find("main")
    if root is not None:
        return root
    return soup.body or soup


def _select_astro_root(soup: BeautifulSoup) -> Tag:
    # STACKIT docs uses Astro + Starlight and renders the content into `.sl-markdown-content`
    # (usually a <div>, not necessarily an <article>).
    root = soup.select_one("main[data-pagefind-body] .sl-markdown-content")
    if root is not None:
        return root
    root = soup.select_one(".sl-markdown-content")
    if root is not None:
        return root
    root = soup.select_one("main article")
    if root is not None:
        return root
    root = soup.find("article")
    if root is not None:
        return root
    root = soup.find("main")
    if root is not None:
        return root
    return soup.body or soup


def _select_generic_root(soup: BeautifulSoup) -> Tag:
    root = soup.find("article")
    if root is not None:
        return root
    root = soup.find("main")
    if root is not None:
        return root
    return soup.body or soup


def docusaurus_sitemap_parser_function(content: Union[str, BeautifulSoup]) -> str:
    """
    Parse Docusaurus pages from a sitemap.

    Given HTML content (as a string or BeautifulSoup object), return the extracted text from the main content area.
    """
    soup = _as_soup(content)
    root = _select_docusaurus_root(soup)
    return _extract_text(root)


def astro_sitemap_parser_function(content: Union[str, BeautifulSoup]) -> str:
    """
    Parse Astro pages from a sitemap.

    Given HTML content (as a string or BeautifulSoup object), return the extracted text from the main content area.
    """
    soup = _as_soup(content)
    root = _select_astro_root(soup)
    return _extract_text(root)


def generic_sitemap_parser_function(content: Union[str, BeautifulSoup]) -> str:
    """
    Parse generic HTML pages from a sitemap.

    This is a safe fallback that tries <article> first, then <main>, and finally the full document body.
    """
    soup = _as_soup(content)
    root = _select_generic_root(soup)
    return _extract_text(root)


def custom_sitemap_parser_function(content: Union[str, BeautifulSoup]) -> str:
    """
    Backwards-compatible sitemap parser.

    Kept for compatibility with existing deployments; defaults to the Docusaurus parser which also works well for many
    other documentation sites.
    """
    return docusaurus_sitemap_parser_function(content)


def _extract_title(soup: BeautifulSoup, root: Tag) -> str:
    h1 = root.find("h1")
    if h1 is None:
        h1 = soup.find("h1")
    if h1 is not None:
        title = h1.get_text(separator=" ", strip=True)
        if title:
            return title

    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        return str(og_title.get("content")).strip()

    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(separator=" ", strip=True)
        if title:
            return title

    return "Unknown Title"


def _title_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = unquote(parsed.path or "").rstrip("/")
    if not path:
        return parsed.hostname or url
    segment = path.split("/")[-1].replace("-", " ").replace("_", " ").strip()
    return segment or url


def docusaurus_sitemap_metadata_parser_function(meta: dict, _content: Any) -> dict:
    """Extract metadata for Docusaurus pages."""
    soup = _as_soup(_content) if isinstance(_content, (str, BeautifulSoup)) else _content
    root = _select_docusaurus_root(soup)
    source_url = meta.get("loc") or meta.get("source")
    title = _extract_title(soup, root)
    if title == "Unknown Title" and source_url:
        title = _title_from_url(str(source_url))
    meta["title"] = title
    return {"source": source_url, **meta} if source_url else meta


def astro_sitemap_metadata_parser_function(meta: dict, _content: Any) -> dict:
    """Extract metadata for Astro pages."""
    soup = _as_soup(_content) if isinstance(_content, (str, BeautifulSoup)) else _content
    root = _select_astro_root(soup)
    source_url = meta.get("loc") or meta.get("source")
    title = _extract_title(soup, root)
    if title == "Unknown Title" and source_url:
        title = _title_from_url(str(source_url))
    meta["title"] = title
    return {"source": source_url, **meta} if source_url else meta


def generic_sitemap_metadata_parser_function(meta: dict, _content: Any) -> dict:
    """Extract metadata for generic HTML pages."""
    soup = _as_soup(_content) if isinstance(_content, (str, BeautifulSoup)) else _content
    root = _select_generic_root(soup)
    source_url = meta.get("loc") or meta.get("source")
    title = _extract_title(soup, root)
    if title == "Unknown Title" and source_url:
        title = _title_from_url(str(source_url))
    meta["title"] = title
    return {"source": source_url, **meta} if source_url else meta


def custom_sitemap_metadata_parser_function(meta: dict, _content: Any) -> dict:
    """Backwards-compatible meta parser."""
    return docusaurus_sitemap_metadata_parser_function(meta, _content)
