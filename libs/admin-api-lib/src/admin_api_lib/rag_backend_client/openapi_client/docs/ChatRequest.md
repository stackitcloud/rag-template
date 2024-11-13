# ChatRequest



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**history** | [**ChatHistory**](ChatHistory.md) |  | [optional] 
**message** | **str** |  | 

## Example

```python
from admin_api_lib.rag_backend_client.openapi_client.models.chat_request import ChatRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ChatRequest from a JSON string
chat_request_instance = ChatRequest.from_json(json)
# print the JSON string representation of the object
print(ChatRequest.to_json())

# convert the object into a dict
chat_request_dict = chat_request_instance.to_dict()
# create an instance of ChatRequest from a dict
chat_request_from_dict = ChatRequest.from_dict(chat_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


