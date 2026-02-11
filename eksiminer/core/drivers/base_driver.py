from abc import ABC, abstractmethod


class DriverClient(ABC):
    @abstractmethod
    def _set_driver(self):
        pass
