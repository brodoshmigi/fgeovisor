from abc import ABC, abstractmethod


class ErrorState(ABC):

    @abstractmethod
    def set_error(self, error_key, value): pass
    
    @abstractmethod
    def send(self): pass