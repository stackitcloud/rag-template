# ExtractionRequest



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**path_on_s3** | **str** |  | 

## Example

```python
from admin_api_lib.extractor_api_client.openapi_client.models.extraction_request import ExtractionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ExtractionRequest from a JSON string
extraction_request_instance = ExtractionRequest.from_json(json)
# print the JSON string representation of the object
print(ExtractionRequest.to_json())

# convert the object into a dict
extraction_request_dict = extraction_request_instance.to_dict()
# create an instance of ExtractionRequest from a dict
extraction_request_from_dict = ExtractionRequest.from_dict(extraction_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


