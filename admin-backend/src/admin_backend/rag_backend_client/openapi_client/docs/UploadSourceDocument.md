# UploadSourceDocument



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_type** | [**ContentType**](ContentType.md) |  | 
**metadata** | [**List[KeyValuePair]**](KeyValuePair.md) |  | 
**content** | **str** |  | 

## Example

```python
from admin_backend.rag_backend_client.openapi_client.models.upload_source_document import UploadSourceDocument

# TODO update the JSON string below
json = "{}"
# create an instance of UploadSourceDocument from a JSON string
upload_source_document_instance = UploadSourceDocument.from_json(json)
# print the JSON string representation of the object
print(UploadSourceDocument.to_json())

# convert the object into a dict
upload_source_document_dict = upload_source_document_instance.to_dict()
# create an instance of UploadSourceDocument from a dict
upload_source_document_from_dict = UploadSourceDocument.from_dict(upload_source_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


