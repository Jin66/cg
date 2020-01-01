from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.bots.nn_bot import NNBot, InputMode
from multiplayer.tron.display.tron_basic_tv import TronBasicTV
from multiplayer.tron.engine import GameEngine
from multiplayer.tron.utils.io import load_object

if __name__ == '__main__':
    old_results_1 = load_object("export/population_live_48_sqrt_diag_100_groups_test.save")
    old_results_2 = load_object("export/population_live_48_sqrt_diag_pos_100_groups_test.save")

    # Get the best ones
    bot1 = NNBot(weights=old_results_1.best_individual.T,
                 can_lose_stupidly=True,
                 input_modes=[
                     InputMode.DistanceSquare,
                     InputMode.DistanceDiag
                 ])
    bot2 = NNBot(weights=old_results_2.best_individual.T,
                 can_lose_stupidly=True,
                 input_modes=[
                     InputMode.DistanceSquare,
                     InputMode.DistanceDiag
                 ])

    # Execute a tron game
    game_engine = GameEngine(debug=False)
    results = game_engine.run([bot1, BasicBot()])
    print(results)

    # Display the game on TV !
    tronTV = TronBasicTV(30, 20)
    tronTV.run(results.moves)
