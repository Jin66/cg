from abc import ABC, abstractmethod


class AbstractFitnessCalculator(ABC):

    @abstractmethod
    def compute(self, population):
        pass
