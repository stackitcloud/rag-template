

from abc import ABC,abstractmethod

from rag_core.models.search_request import SearchRequest
from rag_core.models.search_response import SearchResponse


class Searcher(ABC):
    
    @abstractmethod
    def search(self,search_request: SearchRequest)->SearchResponse:
        pass
