# SourceDocument

Uploading a json with chunks and metadata.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | [**List[KeyValuePair]**](KeyValuePair.md) | The metadata of the documents that are stored in the vectordatabase. | 
**content** | **str** |  | 

## Example

```python
from admin_backend.rag_backend_client.openapi_client.models.source_document import SourceDocument

# TODO update the JSON string below
json = "{}"
# create an instance of SourceDocument from a JSON string
source_document_instance = SourceDocument.from_json(json)
# print the JSON string representation of the object
print(SourceDocument.to_json())

# convert the object into a dict
source_document_dict = source_document_instance.to_dict()
# create an instance of SourceDocument from a dict
source_document_from_dict = SourceDocument.from_dict(source_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


