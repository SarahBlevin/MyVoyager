from abc import ABC, abstractmethod

class datamine(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def report_results(self):
        pass

    @abstractmethod
    def algo(self):
        pass