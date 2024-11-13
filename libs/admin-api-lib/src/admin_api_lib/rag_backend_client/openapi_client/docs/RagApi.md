# admin_api_lib.rag_backend_client.openapi_client.RagApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**chat**](RagApi.md#chat) | **POST** /chat/{session_id} | 
[**evaluate**](RagApi.md#evaluate) | **POST** /evaluate | 
[**remove_information_piece**](RagApi.md#remove_information_piece) | **POST** /information_pieces/remove | remove information piece
[**upload_information_piece**](RagApi.md#upload_information_piece) | **POST** /information_pieces/upload | Upload information pieces for vectordatabase


# **chat**
> ChatResponse chat(session_id, chat_request)



### Example


```python
import admin_api_lib.rag_backend_client.openapi_client
from admin_api_lib.rag_backend_client.openapi_client.models.chat_request import ChatRequest
from admin_api_lib.rag_backend_client.openapi_client.models.chat_response import ChatResponse
from admin_api_lib.rag_backend_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = admin_api_lib.rag_backend_client.openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with admin_api_lib.rag_backend_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = admin_api_lib.rag_backend_client.openapi_client.RagApi(api_client)
    session_id = 'session_id_example' # str | 
    chat_request = admin_api_lib.rag_backend_client.openapi_client.ChatRequest() # ChatRequest | Chat with RAG.

    try:
        api_response = api_instance.chat(session_id, chat_request)
        print("The response of RagApi->chat:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RagApi->chat: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **chat_request** | [**ChatRequest**](ChatRequest.md)| Chat with RAG. | 

### Return type

[**ChatResponse**](ChatResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK. |  -  |
**500** | Internal Server Error! |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **evaluate**
> evaluate()



### Example


```python
import admin_api_lib.rag_backend_client.openapi_client
from admin_api_lib.rag_backend_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = admin_api_lib.rag_backend_client.openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with admin_api_lib.rag_backend_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = admin_api_lib.rag_backend_client.openapi_client.RagApi(api_client)

    try:
        api_instance.evaluate()
    except Exception as e:
        print("Exception when calling RagApi->evaluate: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Accepted. |  -  |
**500** | Internal Server Error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_information_piece**
> remove_information_piece(delete_request)

remove information piece

### Example


```python
import admin_api_lib.rag_backend_client.openapi_client
from admin_api_lib.rag_backend_client.openapi_client.models.delete_request import DeleteRequest
from admin_api_lib.rag_backend_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = admin_api_lib.rag_backend_client.openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with admin_api_lib.rag_backend_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = admin_api_lib.rag_backend_client.openapi_client.RagApi(api_client)
    delete_request = admin_api_lib.rag_backend_client.openapi_client.DeleteRequest() # DeleteRequest | 

    try:
        # remove information piece
        api_instance.remove_information_piece(delete_request)
    except Exception as e:
        print("Exception when calling RagApi->remove_information_piece: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **delete_request** | [**DeleteRequest**](DeleteRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted. |  -  |
**404** | Ressource not Found |  -  |
**422** | ID or metadata missing. |  -  |
**500** | Internal Server Error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_information_piece**
> upload_information_piece(information_piece)

Upload information pieces for vectordatabase

### Example


```python
import admin_api_lib.rag_backend_client.openapi_client
from admin_api_lib.rag_backend_client.openapi_client.models.information_piece import InformationPiece
from admin_api_lib.rag_backend_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = admin_api_lib.rag_backend_client.openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with admin_api_lib.rag_backend_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = admin_api_lib.rag_backend_client.openapi_client.RagApi(api_client)
    information_piece = [admin_api_lib.rag_backend_client.openapi_client.InformationPiece()] # List[InformationPiece] | 

    try:
        # Upload information pieces for vectordatabase
        api_instance.upload_information_piece(information_piece)
    except Exception as e:
        print("Exception when calling RagApi->upload_information_piece: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **information_piece** | [**List[InformationPiece]**](InformationPiece.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | The file was successful uploaded. |  -  |
**422** | Wrong json format. |  -  |
**500** | Internal Server Error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

