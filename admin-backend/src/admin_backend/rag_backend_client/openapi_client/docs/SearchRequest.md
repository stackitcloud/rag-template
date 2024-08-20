# SearchRequest



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**search_term** | **str** |  | 
**metadata** | [**List[KeyValuePair]**](KeyValuePair.md) |  | [optional] 

## Example

```python
from admin_backend.rag_backend_client.openapi_client.models.search_request import SearchRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SearchRequest from a JSON string
search_request_instance = SearchRequest.from_json(json)
# print the JSON string representation of the object
print(SearchRequest.to_json())

# convert the object into a dict
search_request_dict = search_request_instance.to_dict()
# create an instance of SearchRequest from a dict
search_request_from_dict = SearchRequest.from_dict(search_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


