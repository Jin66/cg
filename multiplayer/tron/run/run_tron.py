import cProfile
import logging

import sys

from multiplayer.tron.bots.graph_bot import GraphBot
from multiplayer.tron.engine import GameEngine

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    number_games = 1000
    width = 10
    height = 10
    score = [0, 0, 0, 0]
    seed = None

    logging.basicConfig(stream=sys.stderr, level=logging.WARN)

    for i in range(number_games):
        logging.warning("################### Game %s ###################", i)
        game_engine = GameEngine(debug=False, width=width, height=height)
        results = game_engine.run(
            [GraphBot(width=width, height=height, depth=2),
             GraphBot(width=width, height=height, depth=3),
             GraphBot(width=width, height=height, depth=4),
             GraphBot(width=width, height=height, depth=5)],
            seed=seed)
        print("Match", i, results)
        score[results.winner] += 1
        logging.warning("################### End game %s, score: %s ###################", i, score)

    print(score)

    pr.disable()
    # s = io.StringIO()
    # ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    # ps.print_stats()
    # print(s.getvalue())

    # Depth : [2, 3, 4, 5] => [14, 39, 35, 43]
    # seed: 9999193
