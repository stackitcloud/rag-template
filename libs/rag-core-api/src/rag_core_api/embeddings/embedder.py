from abc import ABC, abstractmethod


class Embedder(ABC):
    @abstractmethod
    def get_embedder(self):
        """return the embedder object"""
