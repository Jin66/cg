import cProfile
import logging

import sys

from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.bots.graph_bot import GraphBot
from multiplayer.tron.engine import GameEngine

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    number_games = 100
    width = 10
    height = 10
    winner = [0, 0, 0, 0]
    seed = None

    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    for i in range(number_games):
        logging.info("################### Game %s ###################", i)
        game_engine = GameEngine(debug=False, width=width, height=height)
        results = game_engine.run(
            [GraphBot(width=width, height=height, depth=3),
             GraphBot(width=width, height=height, depth=6)],
            seed=seed)
        print("Match", i, results)
        winner[results.winner] += 1
        logging.info("################### End game %s, winner: %s ###################", i, results.winner)

    print(winner)

    pr.disable()
    # s = io.StringIO()
    # ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    # ps.print_stats()
    # print(s.getvalue())
