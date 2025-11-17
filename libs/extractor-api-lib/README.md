# extractor-api-lib

Content ingestion layer for the STACKIT RAG template. This library exposes a FastAPI extraction service that ingests raw documents (files or remote sources), extracts and converts (to internal representations) the information, and hands output to [`admin-api-lib`](../admin-api-lib/).

## Responsibilities

- Receive binary uploads and remote source descriptors from the admin backend.
- Route each request through the appropriate extractor (file, sitemap, Confluence, etc.).
- Convert extracted fragments into the shared `InformationPiece` schema expected by downstream services.

## Feature highlights

- **Layered extraction pipeline** – Docling, MarkItDown, and the custom extractors now cooperate with a deterministic fallback chain, so a failed run automatically cascades to the next extractor.
- **Expanded format coverage** – PDFs, Office documents, EPUB, XML, Markdown/AsciiDoc, CSV/TXT, raster images, Confluence spaces, and sitemap-driven websites.
- **Consistent output schema** – Information pieces are returned in a unified structure with content type (`TEXT`, `TABLE`, `IMAGE`) and metadata.
- **Swappable extractors** – Dependency-injector container makes it easy to add or replace file/source extractors, table converters, etc.
- **Production-grade plumbing** – Built-in S3-compatible file service, LangChain loaders with retry/backoff, optional PDF OCR, and throttling controls for web crawls.

## File extractor pipeline

[`GeneralFileExtractor`](src/extractor_api_lib/impl/api_endpoints/general_file_extractor.py) orchestrates file parsing. It resolves the file type from the extension, filters the extractors that declare matching `compatible_file_types`, reverses that filtered list, and then executes the extractors in sequence until one returns content or all have failed. Exceptions are logged and the next extractor takes over; only if every extractor either returns no content or raises an exception do we bubble up an error.

### Default execution order

The dependency container wires extractors in the following list:

1. `DoclingFileExtractor`
2. `MarkitdownFileExtractor`
3. `PDFExtractor`
4. `EpubExtractor`
5. `XMLExtractor`
6. `MSDocsExtractor`
7. `TesseractImageExtractor`

Because the orchestrator reverses the candidate list before the fallback loop, the priority for overlapping formats is the reverse of this wiring. For example, PDFs run through Docling first, then fall back to MarkItDown, and finally to the custom PDF extractor; DOCX/PPTX files follow Docling → MarkItDown → MSDocs; raster images go through Docling’s OCR pipeline before falling back to the Tesseract-only extractor.

### Supported formats

| Format family            | Extensions                                               | Primary extractor          | Fallbacks                                                | Notes |
|--------------------------|----------------------------------------------------------|----------------------------|----------------------------------------------------------|-------|
| PDF                      | `.pdf`                                                   | Docling                    | MarkItDown → Custom PDF extractor                        | Docling performs OCR + table extraction; the PDF extractor keeps Camelot/pdfplumber heuristics as a last resort. |
| Microsoft Word           | `.docx`                                                  | Docling                    | MarkItDown → MSDocs                                      | MSDocs keeps unstructured-based table conversion for custom cases. |
| Microsoft PowerPoint     | `.pptx`                                                  | Docling                    | MarkItDown → MSDocs                                      | MarkItDown splits slides by `<!-- Slide number: N -->`. |
| Microsoft Excel          | `.xlsx`                                                  | Docling                    | —                                                        | Tables returned as markdown; Docling infers sheet structure. |
| EPUB                     | `.epub`                                                  | MarkItDown                 | EPUB extractor                                           | MarkItDown covers simple ebooks; the LangChain-based EPUB extractor preserves metadata when MarkItDown fails. |
| HTML                     | `.html`                                                  | Docling                    | MarkItDown                                               | Docling keeps DOM-aware segmentation; MarkItDown is lighter-weight. |
| Markdown                 | `.md`, `.markdown`, `.mdx`                               | Docling                    | —                                                        | MarkItDown does not currently register for Markdown. |
| AsciiDoc                 | `.adoc`, `.asciidoc`                                     | Docling                    | —                                                        | |
| CSV                      | `.csv`                                                   | Docling                    | MarkItDown                                               | Both produce markdown tables; Docling preserves structured metadata. |
| Plain text               | `.txt`                                                   | MarkItDown                 | —                                                        | |
| XML                      | `.xml`                                                   | XML extractor              | —                                                        | Uses the unstructured XML partitioner. |
| Raster images            | `.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`, `.bmp`          | Docling (OCR)              | Tesseract image extractor                                | Docling feeds Tesseract CLI OCR; the fallback enforces single-frame images via Pillow. |

Image coverage currently excludes animated GIF, WebP, HEIC, and SVG files. These extensions are ignored by the routing logic and will surface as “No extractor found” errors until an extractor declares support.

### Source extractor pipeline

`GeneralSourceExtractor` wires Confluence and sitemap loaders behind a similar abstraction. Unlike files, source extractors are keyed by `ExtractionParameters.source_type` and the matching extractor is called directly (no fallback chain).

## Configuring extractor order

The order lives in `DependencyContainer.file_extractors`. You can override it either by subclassing the container or by overriding the provider at runtime before wiring the FastAPI app. Example:

`container.py`

```python
from dependency_injector.providers import List

from extractor_api_lib.dependency_container import DependencyContainer


class CustomExtractorContainer(DependencyContainer):
    file_extractors = List(
        DependencyContainer.docling_extractor,
        DependencyContainer.markitdown_extractor,
        DependencyContainer.ms_docs_extractor,
        DependencyContainer.pdf_extractor,
        DependencyContainer.image_extractor,
        DependencyContainer.xml_extractor,
        DependencyContainer.epub_extractor,
    )
```

`main.py`

```python
from extractor_api_lib.main import app as perfect_extractor_app, register_dependency_container

from container import CustomExtractorContainer

register_dependency_container(CustomExtractorContainer())
```

The last provider in the list becomes the first extractor tried for a matching file type. Keep shared singleton providers (file service, converters) in the parent class to avoid double instantiation.

## Installation

```bash
pip install extractor-api-lib
```

Python 3.13 is required. OCR and computer-vision features expect system packages such as `ffmpeg`, `poppler-utils`, and `tesseract` (see `services/document-extractor/README.md` for the full list).

## Module tour

- `dependency_container.py` – Central dependency-injector wiring. Override providers here to plug in custom extractors, endpoints etc.
- `api_endpoints/` & `impl/api_endpoints/` – Thin FastAPI endpoint abstractions and implementations for file and source (like confluence & sitemaps) extractors.
- `apis/` – Extractor API abstractions and implementations.
- `extractors/` & `impl/extractors/` – Format-specific logic (PDF, DOCX, PPTX, XML, EPUB, Confluence, sitemap) packaged behind the `InformationExtractor`/`InformationFileExtractor` interfaces.
- `mapper/` & `impl/mapper/` – Abstractions and implementations to map langchain documents, internal and external information piece representations to each other.
- `file_services/` – Default S3-compatible storage adapter; replace it if you store files elsewhere.
- `impl/settings/` – Configuration settings for dependency injection container components.
- `table_converter/` & `impl/table_converter/` – Abstractions and implementations to convert `pandas.DataFrame` to markdown and vice versa.
- `impl/types/` - Enums for content-, extractor- and file types.
- `impl/utils/` – Helper functions for hashed datetime and sitemap crawling, header injection, and custom metadata parsing.

## Endpoints provided

- `POST /extract_from_file` – Downloads the file from S3, extracts its contents, and returns normalized `InformationPiece` records.
- `POST /extract_from_source` – Pulls from remote sources (Confluence, sitemap) using credentials and further optional kwargs.

Both endpoints stream their results back to `admin-api-lib`, which takes care of enrichment and persistence.

## How the file extraction endpoint works

1. Download the file from S3.
2. Derive the file type from the extension (normalizing common image/Markdown/AsciiDoc aliases).
3. Select extractors that declare support for the resolved `FileType`.
4. Run the extractors in priority order (highest priority first); stop at the first non-empty result or keep falling back if an extractor raises.
5. Map the internal representation to the external schema and return the final output.

## How the source extraction endpoint works

1. Chose suitable source extractor based on the source type
2. Pull the source content using the provided credentials and parameters
3. Extract the content from the source
4. Map the internal representation to the external schema
5. Return the final output

## Configuration overview

Two `pydantic-settings` models ship with this package:

- **S3 storage** (`S3Settings`) – configure the built-in file service with `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_ENDPOINT`, and `S3_BUCKET`.

Other extractors accept their parameters at runtime through the request payload (`ExtractionParameters`). For example, the admin backend forwards Confluence credentials, sitemap URLs, or custom headers when it calls `/extract_from_source`. This keeps the library stateless and makes it easy to plug in additional sources without redeploying.

The Helm chart exposes the environment variables mentioned above under `documentExtractor.envs.*` so production deployments remain declarative.

## Typical usage

```python
from extractor_api_lib.main import app as perfect_extractor_app
```

`admin-api-lib` calls `/extract_from_file` and `/extract_from_source` to populate the ingestion pipeline.

## Extending the library

1. Implement `InformationFileExtractor` (for file-based inputs) or `InformationExtractor` (for remote sources).
2. Add a provider to `DependencyContainer` (usually a `Singleton`) and wire dependencies such as the shared `FileService` or table converter.
3. Append the provider to `file_extractors` (or to the source extractor list) in the desired position so that the fallback order is correct.
4. Update mappers or metadata handling if additional fields are required.
5. Cover the happy path and a failure edge case with tests under `libs/extractor-api-lib/tests`, mocking external services (OCR, network, file I/O).

## Advantages and caveats

- Docling-first prioritisation dramatically improves structured extraction (tables, headings) and adds OCR to formats that previously lacked it.
- Retaining MarkItDown and the custom PDF/MS extractors provides graceful degradation when Docling fails or produces empty output.
- Image support now goes through Docling’s OCR before falling back to pure Tesseract.
- The configuration still requires code changes; there is no environment-variable switch to reshuffle or disable extractors at runtime.
- Multi-frame images, animated/novel image formats, and office formats such as ODT/RTF remain unsupported.

## Contributing

Ensure new endpoints or adapters remain thin and defer to [`rag-core-lib`](../rag-core-lib/) for shared logic. Run `poetry run pytest` and the configured linters before opening a PR. For further instructions see the [Contributing Guide](https://github.com/stackitcloud/rag-template/blob/main/CONTRIBUTING.md).

## License

Licensed under the project license. See the root [`LICENSE`](https://github.com/stackitcloud/rag-template/blob/main/LICENSE) file.
