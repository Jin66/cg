from multiplayer.tron.bots.abstract_bot import AbstractBot


class ConstantBot(AbstractBot):

    def get_next_play(self):
        return "UP"

    def get_init_input(self, init):
        pass

    def get_main_input(self, main_lines):
        pass
