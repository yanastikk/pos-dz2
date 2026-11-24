from abc import ABC, abstractmethod


class ResultExporter(ABC):
    @abstractmethod
    def export(self, grades):
        pass
