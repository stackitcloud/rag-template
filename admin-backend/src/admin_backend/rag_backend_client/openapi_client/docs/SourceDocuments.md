# SourceDocuments



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documents** | [**List[SourceDocument]**](SourceDocument.md) |  | 

## Example

```python
from admin_backend.rag_backend_client.openapi_client.models.source_documents import SourceDocuments

# TODO update the JSON string below
json = "{}"
# create an instance of SourceDocuments from a JSON string
source_documents_instance = SourceDocuments.from_json(json)
# print the JSON string representation of the object
print(SourceDocuments.to_json())

# convert the object into a dict
source_documents_dict = source_documents_instance.to_dict()
# create an instance of SourceDocuments from a dict
source_documents_from_dict = SourceDocuments.from_dict(source_documents_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


