from abc import ABC, abstractmethod


class StoreOwnedModel(ABC):
    """
    Contract for models that belong to a store.
    """

    @abstractmethod
    def get_store(self):
        pass