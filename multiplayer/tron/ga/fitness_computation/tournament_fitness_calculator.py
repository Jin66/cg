import enum

from multiplayer.tron.ga.fitness_computation.abstract_fitness_calculator import AbstractFitnessCalculator


class FitnessMode(enum.Enum):
    Winner = 1
    LiveDuration = 2


class TournamentFitnessCalculator(AbstractFitnessCalculator):

    def __init__(self, bot_create_function, game_engine, fitness_mode=FitnessMode.LiveDuration):
        self.game_engine = game_engine
        self.bot_create_function = bot_create_function
        self.fitness_mode = fitness_mode

    def compute(self, population):
        # For now each individual play a game against all the other bots in a 1 vs 1 match.
        score = [0 for i in population]
        for individual_id in range(len(population) - 1):
            for opponent_id in range(individual_id + 1, len(population)):
                result = self.run_match([individual_id, opponent_id], population)
                if self.fitness_mode == FitnessMode.Winner:
                    if result.winner == 0:
                        score[individual_id] += 1
                    else:
                        score[opponent_id] += 1
                if self.fitness_mode == FitnessMode.LiveDuration:
                    if result.winner == 0:
                        score[individual_id] += 500
                        score[opponent_id] += result.lives_duration[1]
                    else:
                        score[opponent_id] += 500
                        score[individual_id] += result.lives_duration[0]
        if self.fitness_mode == FitnessMode.LiveDuration:
            for i in range(len(population)):
                score[i] /= len(population)
        print("Results tournament: ", score)
        return score

    def run_match(self, ids_population, population):
        # Generate bot list
        bots_list = []
        for id_population in ids_population:
            bots_list.append(self.bot_create_function(population[id_population, :].T))

        # Create game engine
        return self.game_engine.run(bots_list)
