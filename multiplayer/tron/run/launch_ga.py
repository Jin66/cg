import cProfile
import io
import pstats

from matplotlib import pyplot as plt

from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.bots.nn_bot import NNBot, InputMode
from multiplayer.tron.engine import GameEngine
from multiplayer.tron.ga.basic_genetic_algorithm import BasicGeneticAlgorithm
from multiplayer.tron.ga.fitness_computation.basic_fitness_calculator import BasicFitnessCalculator, FitnessMode
from multiplayer.tron.utils.io import save_object, load_object

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    # Import/export settings
    file_name_save = "export/population_live.save"
    population_saved = load_object(file_name_save)

    # Fitness calculator
    bot_create_function = lambda weight: NNBot(weights=weight,
                                               can_lose_stupidly=False,
                                               input_modes=[InputMode.DistanceSquare,
                                                            InputMode.DistanceDiag,
                                                            InputMode.BotsPosition]
                                               )
    opponent_create_function = BasicBot
    # fitness_calculator = TournamentFitnessCalculator(bot_create_function, GameEngine())
    fitness_calculator = BasicFitnessCalculator(bot_create_function, opponent_create_function, GameEngine(),
                                                nb_matchs=10,
                                                fitness_mode=FitnessMode.Winner)
    tournamentGeneticAlgorithm = BasicGeneticAlgorithm(400, fitness_calculator,
                                                       population=population_saved,
                                                       genes_size=64
                                                       )
    results = tournamentGeneticAlgorithm.run()
    save_object(results["population"], file_name_save)

    plt.plot(results["fitness"])
    plt.show()

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print(s.getvalue())
