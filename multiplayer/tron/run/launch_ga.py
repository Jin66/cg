import cProfile
import io
import pstats

from matplotlib import pyplot as plt

from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.bots.nn_bot import NNBot, InputMode
from multiplayer.tron.engine import GameEngine
from multiplayer.tron.ga.basic_genetic_algorithm import BasicGeneticAlgorithm
from multiplayer.tron.ga.fitness_computation.basic_fitness_calculator import BasicFitnessCalculator, FitnessMode
from multiplayer.tron.ga.fitness_computation.tournament_fitness_calculator import TournamentFitnessCalculator
from multiplayer.tron.utils.io import save_object, load_object

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    # Fitness calculator
    bot_create_function = lambda weight: NNBot(weights=weight,
                                               can_lose_stupidly=True,
                                               input_modes=[InputMode.DistanceSquare,
                                                            InputMode.DistanceDiag,
                                                            InputMode.BotsPosition]
                                               )
    opponent_create_function = BasicBot
    fitness_calculator_tournament = TournamentFitnessCalculator(bot_create_function, GameEngine())
    fitness_calculator_basic = BasicFitnessCalculator(bot_create_function, opponent_create_function, GameEngine(),
                                                      nb_matchs=5,
                                                      fitness_mode=FitnessMode.LiveDuration)

    file_name_save = "export/population_live.save"
    for turn in range(20):
        old_results = load_object(file_name_save)
        tournamentGeneticAlgorithm = BasicGeneticAlgorithm(20, fitness_calculator_tournament,
                                                           ga_results=old_results,
                                                           genes_size=64,
                                                           genes_groups=[[i * 4, (i + 1) * 4] for i in range(16)]
                                                           )
        results = tournamentGeneticAlgorithm.run()
        save_object(results, file_name_save)

    plt.plot(results["fitness_best"])
    plt.show()

    plt.plot(results["fitness_mean"])
    plt.show()

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print(s.getvalue())
