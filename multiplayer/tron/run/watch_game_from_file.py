from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.display.tron_basic_tv import TronBasicTV
from multiplayer.tron.engine import GameEngine
from multiplayer.tron.utils.io import load_object

if __name__ == '__main__':

    # Load match
    file_name_save = "export/match.save"
    results = load_object(file_name_save)

    # Display the game on TV !
    tronTV = TronBasicTV(30, 20)
    tronTV.run(results.moves)
