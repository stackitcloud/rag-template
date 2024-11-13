# InformationPiece

Uploading a json with chunks and metadata.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | [**List[KeyValuePair]**](KeyValuePair.md) | The metadata of the documents that are stored in the vectordatabase. | 
**page_content** | **str** | The content of the document | 
**type** | [**ContentType**](ContentType.md) |  | 

## Example

```python
from admin_api_lib.rag_backend_client.openapi_client.models.information_piece import InformationPiece

# TODO update the JSON string below
json = "{}"
# create an instance of InformationPiece from a JSON string
information_piece_instance = InformationPiece.from_json(json)
# print the JSON string representation of the object
print(InformationPiece.to_json())

# convert the object into a dict
information_piece_dict = information_piece_instance.to_dict()
# create an instance of InformationPiece from a dict
information_piece_from_dict = InformationPiece.from_dict(information_piece_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


