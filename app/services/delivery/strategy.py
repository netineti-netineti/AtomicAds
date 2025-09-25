from abc import ABC, abstractmethod


class DeliveryStrategy(ABC):
    @abstractmethod
    def send(self, alert, user):
        raise NotImplementedError