from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.display.tron_basic_tv import TronBasicTV
from multiplayer.tron.engine import GameEngine

if __name__ == '__main__':

    # Execute a simple game
    game_engine = GameEngine(debug=True)
    results = game_engine.run([BasicBot(), BasicBot(), BasicBot(), BasicBot()])
    print(results)

    # Display the game on TV !
    tronTV = TronBasicTV(30, 20)
    tronTV.run(results.moves)
