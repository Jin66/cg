from matplotlib import pyplot as plt

from multiplayer.tron.bots.basic_bot import BasicBot
from multiplayer.tron.bots.nn_bot import NNBot, InputMode
from multiplayer.tron.engine import GameEngine
from multiplayer.tron.ga.basic_genetic_algorithm import BasicGeneticAlgorithm, OffspringGroup
from multiplayer.tron.ga.fitness_computation.basic_fitness_calculator import BasicFitnessCalculator, FitnessMode
from multiplayer.tron.ga.fitness_computation.tournament_fitness_calculator import TournamentFitnessCalculator
from multiplayer.tron.utils.io import load_object, save_object

if __name__ == '__main__':
    # pr = cProfile.Profile()
    # pr.enable()

    # Fitness calculator
    bot_create_function = lambda weight: NNBot(weights=weight,
                                               can_lose_stupidly=True,
                                               input_modes=[
                                                   InputMode.DistanceSquare,
                                                   InputMode.DistanceDiag
                                               ]
                                               )
    opponent_create_function = BasicBot
    fitness_calculator_tournament = TournamentFitnessCalculator(bot_create_function, GameEngine(debug=False))
    fitness_calculator_basic = BasicFitnessCalculator(bot_create_function, opponent_create_function,
                                                      GameEngine(debug=False),
                                                      nb_matchs=20,
                                                      fitness_mode=FitnessMode.LiveDuration)

    file_name_import = "export/population_tournament_sqrt_diag_100_test.save"
    file_name_export = "export/population_tournament_sqrt_diag_100_test.save"
    nn_in = 8
    nn_out = 4
    # Group based on input:  genes_groups = [[i * nn_out, (i + 1) * nn_out] for i in range(nn_in)]
    # Group based on output: genes_groups = [[i + (nn_out*j) for j in range(nn_in)] for i in range(nn_out)]

    results = load_object(file_name_import)
    for turn in range(10):
        tournamentGeneticAlgorithm = BasicGeneticAlgorithm(20, fitness_calculator_basic,
                                                           ga_results=results,
                                                           genes_size=nn_in * nn_out,
                                                           genes_groups=[[i * nn_out, (i + 1) * nn_out] for i in
                                                                         range(nn_in)],
                                                           offspring_groups=[OffspringGroup(20, 0.9, 1.1),
                                                                             OffspringGroup(20, 0.4, 0.6),
                                                                             OffspringGroup(20, 0.2, 0)]
                                                           )
        results = tournamentGeneticAlgorithm.run()
        save_object(results, file_name_export)

    plt.plot(results.fitness_best)
    plt.show()

    plt.plot(results.fitness_mean)
    plt.show()

    # pr.disable()
    # s = io.StringIO()
    # ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    # ps.print_stats()
    # print(s.getvalue())
