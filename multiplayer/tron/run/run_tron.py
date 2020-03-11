import cProfile
import io
import logging
import pstats

import sys

from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.bots.graph_bot import GraphBot
from multiplayer.tron.engine import GameEngine

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    number_games = 1
    width = 6
    height = 4
    score = [0, 0, 0, 0]
    seed = None
    logging.basicConfig(stream=sys.stderr, level=logging.WARN)

    for i in range(number_games):
        logging.warning("################### Game %s ###################", i)
        game_engine = GameEngine(debug=False, width=width, height=height)
        results = game_engine.run(
            [BasicBot(width=width, height=height),
             GraphBot(width=width, height=height, depth=1)
             ],
            seed=seed)
        print("Match", i, results)
        score[results.winner] += 1
        logging.warning("################### End game %s, score: %s ###################", i, score)

    logging.info(score)

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print(s.getvalue())

    # Depth : [2, 3, 4, 5] => [14, 39, 35, 43]
    # seed: 9999193
