# admin_backend.rag_backend_client.openapi_client.RagApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**chat**](RagApi.md#chat) | **POST** /chat/{session_id} | 
[**remove_source_documents**](RagApi.md#remove_source_documents) | **POST** /source_documents/remove | 
[**search**](RagApi.md#search) | **POST** /search | 
[**upload_source_documents**](RagApi.md#upload_source_documents) | **POST** /source_documents | Upload Files for RAG.


# **chat**
> ChatResponse chat(session_id, chat_request)



### Example


```python
import admin_backend.rag_backend_client.openapi_client
from admin_backend.rag_backend_client.openapi_client.models.chat_request import ChatRequest
from admin_backend.rag_backend_client.openapi_client.models.chat_response import ChatResponse
from admin_backend.rag_backend_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = admin_backend.rag_backend_client.openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with admin_backend.rag_backend_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = admin_backend.rag_backend_client.openapi_client.RagApi(api_client)
    session_id = 'session_id_example' # str | 
    chat_request = admin_backend.rag_backend_client.openapi_client.ChatRequest() # ChatRequest | Chat with RAG.

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

# **remove_source_documents**
> remove_source_documents(delete_request)



### Example


```python
import admin_backend.rag_backend_client.openapi_client
from admin_backend.rag_backend_client.openapi_client.models.delete_request import DeleteRequest
from admin_backend.rag_backend_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = admin_backend.rag_backend_client.openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with admin_backend.rag_backend_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = admin_backend.rag_backend_client.openapi_client.RagApi(api_client)
    delete_request = admin_backend.rag_backend_client.openapi_client.DeleteRequest() # DeleteRequest | 

    try:
        api_instance.remove_source_documents(delete_request)
    except Exception as e:
        print("Exception when calling RagApi->remove_source_documents: %s\n" % e)
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

# **search**
> SearchResponse search(search_request)



### Example


```python
import admin_backend.rag_backend_client.openapi_client
from admin_backend.rag_backend_client.openapi_client.models.search_request import SearchRequest
from admin_backend.rag_backend_client.openapi_client.models.search_response import SearchResponse
from admin_backend.rag_backend_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = admin_backend.rag_backend_client.openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with admin_backend.rag_backend_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = admin_backend.rag_backend_client.openapi_client.RagApi(api_client)
    search_request = admin_backend.rag_backend_client.openapi_client.SearchRequest() # SearchRequest | 

    try:
        api_response = api_instance.search(search_request)
        print("The response of RagApi->search:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RagApi->search: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_request** | [**SearchRequest**](SearchRequest.md)|  | 

### Return type

[**SearchResponse**](SearchResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | 200. |  -  |
**500** | Internal Server Error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_source_documents**
> upload_source_documents(upload_source_document)

Upload Files for RAG.

### Example


```python
import admin_backend.rag_backend_client.openapi_client
from admin_backend.rag_backend_client.openapi_client.models.upload_source_document import UploadSourceDocument
from admin_backend.rag_backend_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = admin_backend.rag_backend_client.openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with admin_backend.rag_backend_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = admin_backend.rag_backend_client.openapi_client.RagApi(api_client)
    upload_source_document = [admin_backend.rag_backend_client.openapi_client.UploadSourceDocument()] # List[UploadSourceDocument] | 

    try:
        # Upload Files for RAG.
        api_instance.upload_source_documents(upload_source_document)
    except Exception as e:
        print("Exception when calling RagApi->upload_source_documents: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upload_source_document** | [**List[UploadSourceDocument]**](UploadSourceDocument.md)|  | 

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

