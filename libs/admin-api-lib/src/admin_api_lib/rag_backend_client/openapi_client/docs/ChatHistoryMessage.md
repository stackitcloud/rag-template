# ChatHistoryMessage



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | [**ChatRole**](ChatRole.md) |  | 
**message** | **str** |  | 

## Example

```python
from admin_api_lib.rag_backend_client.openapi_client.models.chat_history_message import ChatHistoryMessage

# TODO update the JSON string below
json = "{}"
# create an instance of ChatHistoryMessage from a JSON string
chat_history_message_instance = ChatHistoryMessage.from_json(json)
# print the JSON string representation of the object
print(ChatHistoryMessage.to_json())

# convert the object into a dict
chat_history_message_dict = chat_history_message_instance.to_dict()
# create an instance of ChatHistoryMessage from a dict
chat_history_message_from_dict = ChatHistoryMessage.from_dict(chat_history_message_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


