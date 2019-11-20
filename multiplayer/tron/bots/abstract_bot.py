from abc import ABC, abstractmethod


class AbstractBot(ABC):

    @abstractmethod
    def get_init_input(self, init):
        pass

    @abstractmethod
    def get_main_input(self, main_lines):
        pass

    @abstractmethod
    def get_next_play(self):
        pass
