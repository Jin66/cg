import cProfile
import io
import pstats

from matplotlib import pyplot as plt

from multiplayer.tron.genetic_algorithms.tournament_genetic_algorithm import TournamentGeneticAlgorithm
from multiplayer.tron.utils.io import save_object, load_object

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    file_name_save = "../export/population_square_pos_not_cls.save"
    population_saved = load_object(file_name_save)
    tournamentGeneticAlgorithm = TournamentGeneticAlgorithm(200, population=population_saved)
    results = tournamentGeneticAlgorithm.run()
    save_object(results["population"], file_name_save)

    plt.plot(results["fitness"])
    plt.show()

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print(s.getvalue())
