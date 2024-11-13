# ChatResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**answer** | **str** |  | 
**finish_reason** | **str** |      | 
**citations** | [**List[InformationPiece]**](InformationPiece.md) |  | 

## Example

```python
from admin_api_lib.rag_backend_client.openapi_client.models.chat_response import ChatResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ChatResponse from a JSON string
chat_response_instance = ChatResponse.from_json(json)
# print the JSON string representation of the object
print(ChatResponse.to_json())

# convert the object into a dict
chat_response_dict = chat_response_instance.to_dict()
# create an instance of ChatResponse from a dict
chat_response_from_dict = ChatResponse.from_dict(chat_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


