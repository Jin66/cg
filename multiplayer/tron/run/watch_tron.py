from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.bots.graph_bot import GraphBot
from multiplayer.tron.bots.graph_bot_old import GraphBotOld
from multiplayer.tron.bots.smart_bot import SmartBot
from multiplayer.tron.display.tron_basic_tv import TronBasicTV
from multiplayer.tron.engine import GameEngine

if __name__ == '__main__':

    width = 20
    height = 20

    # Execute a simple game
    bot_list4 = [BasicBot(width=width, height=height), GraphBot(width=width, height=height), BasicBot(width=width, height=height), BasicBot(width=width, height=height)]
    bot_list = [GraphBot(width=width, height=height, depth=1), GraphBot(width=width, height=height, depth=3)]

    # Execute the game
    seed = 1263213
    game_engine = GameEngine(debug=False, width=width, height=height)
    results = game_engine.run(
        [GraphBotOld(width=width, height=height, depth=1),
         GraphBot(width=width, height=height, depth=1)
         ], seed=seed)
    print(results)

    # Display the game on TV !
    tronTV = TronBasicTV(width, height)
    tronTV.run(results.moves)
