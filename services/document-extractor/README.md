# Document Extractor
The document extractor parses uploaded documents and remote sources (for example Confluence or sitemaps). It is not exposed by ingress and only for internal use.

The following endpoints are provided by the *document-extractor*:
- `/extract_from_file`: Extracts information from files stored in object storage.
- `/extract_from_source`: Extracts information from non-file sources such as Confluence or sitemaps.

# Requirements
All required python libraries can be found in the [pyproject.toml](pyproject.toml) file.
In addition to python libraries the following system packages are required:

```shell
build-essential
make
ffmpeg
poppler-utils
tesseract-ocr
tesseract-ocr-deu
tesseract-ocr-eng
libleptonica-dev
pkg-config
```

The Tesseract data path is set via `TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata` in both prod and dev images.

# Endpoints

## `/extract_from_file`
The file extraction endpoint loads files from the connected storage and extracts information from supported formats (PDF, Office, EPUB, XML, images, etc.).
The following types of information can be extracted:
- `TEXT`: plain text
- `TABLE`: data in tabular form found in the document
- `IMAGE`: images found in the document (when supported)

## `/extract_from_source`
The source extraction endpoint loads content from non-file sources (for example Confluence or sitemaps). The extracted information depends on the source and may include:
- `TEXT`: plain text
- `TABLE`: data in tabular form found on a page
- `IMAGE`: images found on a page

For details on supported formats and source-specific parameters (such as sitemap filters or `continue_on_failure`), see the [extractor API lib README](../../libs/extractor-api-lib/README.md).

## Deployment

A detailed explanation of the deployment can be found in the [project README](../../README.md).
The *helm-chart* used for the deployment can be found in the [infrastructure directory](../../infrastructure/).
