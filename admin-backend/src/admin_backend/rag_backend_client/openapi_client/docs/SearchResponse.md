# SearchResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documents** | [**List[SourceDocument]**](SourceDocument.md) |  | 
**answer** | **str** |  | 
**finish_reason** | **str** |      | 
**citations** | [**List[SourceDocument]**](SourceDocument.md) |  | 

## Example

```python
from admin_backend.rag_backend_client.openapi_client.models.search_response import SearchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SearchResponse from a JSON string
search_response_instance = SearchResponse.from_json(json)
# print the JSON string representation of the object
print(SearchResponse.to_json())

# convert the object into a dict
search_response_dict = search_response_instance.to_dict()
# create an instance of SearchResponse from a dict
search_response_from_dict = SearchResponse.from_dict(search_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


