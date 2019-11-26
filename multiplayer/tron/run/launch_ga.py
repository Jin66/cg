import cProfile
import io
import pstats

from matplotlib import pyplot as plt

from multiplayer.tron.bots.nn_bot import NNBot, InputMode
from multiplayer.tron.engine import GameEngine
from multiplayer.tron.ga.basic_genetic_algorithm import BasicGeneticAlgorithm, FitnessMode
from multiplayer.tron.ga.fitness_computation.tournament_fitness_calculator import TournamentFitnessCalculator
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
    fitness_calculator = TournamentFitnessCalculator(bot_create_function, GameEngine())
    tournamentGeneticAlgorithm = BasicGeneticAlgorithm(400, fitness_calculator, population=population_saved)
    results = tournamentGeneticAlgorithm.run()
    save_object(results["population"], file_name_save)

    plt.plot(results["fitness"])
    plt.show()

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print(s.getvalue())
