import enum
import statistics

from multiplayer.tron.ga.fitness_computation.abstract_fitness_calculator import AbstractFitnessCalculator


class FitnessMode(enum.Enum):
    Winner = 1
    LiveDuration = 2


class BasicFitnessCalculator(AbstractFitnessCalculator):

    def __init__(self, bot_create_function, opponent_create_function, game_engine,
                 fitness_mode=FitnessMode.LiveDuration, nb_matchs=2):
        self.nb_matchs = nb_matchs
        self.opponent_create_function = opponent_create_function
        self.game_engine = game_engine
        self.bot_create_function = bot_create_function
        self.fitness_mode = fitness_mode

    def compute(self, population):
        # For now each individual play a 2 players game, a 3 player game, a 4 player game
        score = [0 for i in population]
        for opp_number in [1, 2, 3]:
            for individual_id in range(len(population) - 1):
                for match_number in range(self.nb_matchs):
                    result = self.run_match(individual_id, population, opp_number)
                    if self.fitness_mode == FitnessMode.Winner:
                        if result.winner == 0:
                            score[individual_id] += 1
                    if self.fitness_mode == FitnessMode.LiveDuration:
                        if result.winner == 0:
                            score[individual_id] += 500
                        else:
                            score[individual_id] += result.lives_duration[0]
        if self.fitness_mode == FitnessMode.LiveDuration:
            for i in range(len(population)):
                score[i] /= 3 * self.nb_matchs
        return score

    def run_match(self, id_population, population, nb_opponent):
        # Generate bot list
        bots_list = [self.bot_create_function(population[id_population, :].T)]
        for i in range(nb_opponent):
            bots_list.append(self.opponent_create_function())

        # Create game engine
        return self.game_engine.run(bots_list)
