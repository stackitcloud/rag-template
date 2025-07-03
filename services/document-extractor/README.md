# Document Extractor
The document extractor job is to parse the uploaded documents. It is not exposed by ingress and only for internal use.

The following endpoints are provided by the *documents_extractor*:
- `/extract`: This endpoint extracts the information from pdf files.

# Requirements
All required python libraries can be found in the [pyproject.toml](pyproject.toml) file.
In addition to python libraries the following system packages are required:
```
build-essential
make
ffmpeg
poppler-utils
tesseract-ocr
tesseract-ocr-deu
tesseract-ocr-eng
```

# Endpoints

## `/extract`
The extract endpoint will extract the information from PDF files.
It requires the path to the file on the connected storage.
The following types of information will be extracted:
- `TEXT`: plain text
- `TABLE`: data in tabular form found in the document

# Deployment
A detailed explanation of the deployment can be found in the [Readme](../README.md) of the project.
The *helm-chart* used for the deployment can be found [here](../helm-chart/charts/admin-backend/).


