# extractor-api-lib

Content ingestion layer for the STACKIT RAG template. This library exposes a FastAPI extraction service that ingests raw documents (files or remote sources), extracts and converts (to internal representations) the information, and hands output to [`admin-api-lib`](../admin-api-lib/).

## Responsibilities

- Receive binary uploads and remote source descriptors from the admin backend.
- Route each request through the appropriate extractor (file, sitemap, Confluence, etc.).
- Convert extracted fragments into the shared `InformationPiece` schema expected by downstream services.

## Feature highlights

- **Broad format coverage** – PDFs, DOCX, PPTX, XML/EPUB, Confluence spaces, and sitemap-driven websites.
- **Consistent output schema** – Information pieces are returned in a unified structure with content type (`TEXT`, `TABLE`, `IMAGE`) and metadata.
- **Swappable extractors** – Dependency-injector container makes it easy to add or replace file/source extractors, table converters, etc.
- **Production-grade plumbing** – Built-in S3-compatible file service, LangChain loaders with retry/backoff, optional PDF OCR, and throttling controls for web crawls.

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

1. Download the file from S3
2. Chose suitable file extractor based on the filename ending
3. Extract the content from the file
4. Map the internal representation to the external schema
5. Return the final output

## How the source extraction endpoint works

1. Chose suitable source extractor based on the source type
2. Pull the source content using the provided credentials and parameters
3. Extract the content from the source
4. Map the internal representation to the external schema
5. Return the final output

## Configuration overview

Two `pydantic-settings` models ship with this package:

- **S3 storage** (`S3Settings`) – configure the built-in file service with `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_ENDPOINT`, and `S3_BUCKET`.
- **PDF extraction** (`PDFExtractorSettings`) – adjust footer trimming or diagram export via `PDF_EXTRACTOR_FOOTER_HEIGHT` and `PDF_EXTRACTOR_DIAGRAMS_FOLDER_NAME`.

Other extractors accept their parameters at runtime through the request payload (`ExtractionParameters`). For example, the admin backend forwards Confluence credentials, sitemap URLs, or custom headers when it calls `/extract_from_source`. This keeps the library stateless and makes it easy to plug in additional sources without redeploying.

The Helm chart exposes the environment variables mentioned above under `documentExtractor.envs.*` so production deployments remain declarative.

## Typical usage

```python
from extractor_api_lib.main import app as perfect_extractor_app
```

`admin-api-lib` calls `/extract_from_file` and `/extract_from_source` to populate the ingestion pipeline.

## Extending the library

1. Implement `InformationFileExtractor` or `InformationExtractor` for your new format/source.
2. Register it in `dependency_container.py` (append to `file_extractors` list or `source_extractors` dict).
3. Update mapper or metadata handling if additional fields are required.
4. Add unit tests under `libs/extractor-api-lib/tests` using fixtures and fake storage providers.

## Contributing

Ensure new endpoints or adapters remain thin and defer to [`rag-core-lib`](../rag-core-lib/) for shared logic. Run `poetry run pytest` and the configured linters before opening a PR. For further instructions see the [Contributing Guide](https://github.com/stackitcloud/rag-template/blob/main/CONTRIBUTING.md).

## License

Licensed under the project license. See the root [`LICENSE`](https://github.com/stackitcloud/rag-template/blob/main/LICENSE) file.
