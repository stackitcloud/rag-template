from bs4 import BeautifulSoup
from typing import Any, Union


def custom_sitemap_parser_function(content: Union[str, BeautifulSoup]) -> str:
    """
    Given HTML content (as a string or BeautifulSoup object), return only the
    concatenated text from all <article> elements.

    Parameters
    ----------
    content : Union[str, BeautifulSoup]
        The HTML content to parse, either as a string or a BeautifulSoup object.
    """
    if isinstance(content, str):
        soup = BeautifulSoup(content, "html.parser")
    else:
        soup = content

    article_elements = soup.find_all("article")
    if not article_elements:
        return str(content.get_text())

    texts = [element.get_text(separator=" ", strip=True) for element in article_elements]
    return "\n".join(texts)


def custom_sitemap_metadata_parser_function(meta: dict, _content: Any) -> dict:
    """
    Given metadata and HTML content, extract the title from the first article and the first <h1> element

    Parameters
    ----------
    meta : dict
        Metadata dictionary containing the source location and other metadata.
    _content : Any
        The HTML content to parse
    """
    if isinstance(_content, str):
        soup = BeautifulSoup(_content, "html.parser")
    else:
        soup = _content

    article_elements = soup.find_all("article")
    if not article_elements:
        return {"source": meta["loc"], **meta}

    # Find h1 elements within the first article element
    h1_elements = article_elements[0].find_all("h1")
    meta["title"] = h1_elements[0].get_text(strip=True) if h1_elements else "Unknown Title"
    return {"source": meta["loc"], **meta}
