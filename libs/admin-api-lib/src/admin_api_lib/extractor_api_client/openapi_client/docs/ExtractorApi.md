# admin_api_lib.extractor_api_client.openapi_client.ExtractorApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**extract_information**](ExtractorApi.md#extract_information) | **POST** /extract | 


# **extract_information**
> List[InformationPiece] extract_information(extraction_request)



### Example


```python
import admin_api_lib.extractor_api_client.openapi_client
from admin_api_lib.extractor_api_client.openapi_client.models.extraction_request import ExtractionRequest
from admin_api_lib.extractor_api_client.openapi_client.models.information_piece import InformationPiece
from admin_api_lib.extractor_api_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = admin_api_lib.extractor_api_client.openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with admin_api_lib.extractor_api_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = admin_api_lib.extractor_api_client.openapi_client.ExtractorApi(api_client)
    extraction_request = admin_api_lib.extractor_api_client.openapi_client.ExtractionRequest() # ExtractionRequest | 

    try:
        api_response = api_instance.extract_information(extraction_request)
        print("The response of ExtractorApi->extract_information:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExtractorApi->extract_information: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **extraction_request** | [**ExtractionRequest**](ExtractionRequest.md)|  | 

### Return type

[**List[InformationPiece]**](InformationPiece.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of extracted information. |  -  |
**422** | Body is not a valid PDF. |  -  |
**500** | Something somewhere went terribly wrong. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

