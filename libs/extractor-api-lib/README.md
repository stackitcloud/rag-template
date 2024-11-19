# Extractor API Lib
The Extractor Library contains a default implementation and provides document parsing capabilities for various file formats. It is not exposed by ingress and only for internal use.

The following endpoints are provided by the *documents_extractor*:
- `/extract_from_file`: This endpoint extracts the information from PDF,PTTX,WORD,XML files.
- `/extract_from_confluence`: This endpoint extracts the information from a confluence space.

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

## `/extract_from_file`
The extract from file endpoint will extract the information from PDF,PTTX,WORD,XML files.
It requires the path to the file on the connected storage.
The following types of information will be extracted:
- `TEXT`: plain text
- `TABLE`: data in tabular form found in the document

## `/extract_from_confluence`
The extract from confluence endpoint will extract the information from a confluence space.
It requires the the credentials to the confluence space.
The following types of information will be extracted:
- `TEXT`: plain text

# Deployment
A detailed explanation of the deployment can be found in the [Readme](../README.md) of the project.
The *helm-chart* used for the deployment can be found [here](../helm-chart/charts/admin-backend/).


