from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.bots.graph_bot import GraphBot
from multiplayer.tron.bots.smart_bot import SmartBot
from multiplayer.tron.display.tron_basic_tv import TronBasicTV
from multiplayer.tron.engine import GameEngine

if __name__ == '__main__':

    width = 30
    height = 20

    # Execute a simple game
    game_engine = GameEngine(debug=False, width=width, height=height)
    results = game_engine.run([BasicBot(width=width, height=height), GraphBot(width=width, height=height)])
    print(results)

    # Display the game on TV !
    tronTV = TronBasicTV(width, height)
    tronTV.run(results.moves)
