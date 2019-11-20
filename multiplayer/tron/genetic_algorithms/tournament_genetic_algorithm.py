import numpy as np

from multiplayer.tron.bots.nn_bot import NNBot, InputMode
from multiplayer.tron.engine import GameEngine


class TournamentGeneticAlgorithm:
    population_size = 50
    uniform_params = 4
    genes_size = 48
    number_parents = 20
    number_offspring = 20
    mutation_factor = 2

    def __init__(self, number_generation, population=None):
        self.number_generation = number_generation

        if population is None:
            print("Creating random population...")
            self.init_population(self.population_size)
        else:
            print("Using imported population...(", len(population), ")")
            self.population = population

    def init_population(self, population_size):
        self.population = self.get_random_individuals(self.population_size)

    def get_random_individuals(self, size):
        return np.random.uniform(low=-self.uniform_params, high=self.uniform_params, size=(size, self.genes_size))

    def run(self):
        results = {"fitness": []}
        for generation in range(self.number_generation):
            print("Generation:", generation)
            fitness_population = self.launch_tournament()
            index_best = np.argsort(fitness_population)
            results["fitness"].append(fitness_population[index_best[-1]])
            print("Best fitness:", fitness_population[index_best[-1]])
            print(self.population[index_best[-1]])
            parents = self.selection(fitness_population, self.number_parents, index_best)
            offspring = self.crossover(parents, (self.number_offspring, self.genes_size))
            mutated_offspring = self.mutate(offspring)
            self.population[0:self.number_parents, :] = parents
            self.population[self.number_parents:self.number_parents + self.number_offspring, :] = mutated_offspring

            filing_size = self.population_size - (self.number_parents + self.number_offspring)
            self.population[self.number_parents + self.number_offspring:, :] = self.get_random_individuals(filing_size)
        index_best_parent = np.argsort(fitness_population)[-1]
        results["best_individual"] = self.population[index_best_parent]
        results["population"] = self.population
        return results

    def launch_tournament(self):
        # For now each individual play a game against all the other bots in a 1 vs 1 match.
        score = [0 for i in self.population]
        for individual_id in range(len(self.population) - 1):
            for opponent_id in range(individual_id + 1, len(self.population)):
                match_scores = self.run_match([individual_id, opponent_id])
                score[individual_id] += match_scores[0]
                score[opponent_id] += match_scores[1]
        for i in range(len(self.population)):
            score[i] /= len(self.population)
        return score

    def run_match(self, ids_population):
        # Generate bot list
        bots_list = []
        for id_population in ids_population:
            bots_list.append(
                NNBot(weights=self.population[id_population, :].T,
                      can_lose_stupidly=True,
                      input_modes=[InputMode.DistanceSquare, InputMode.DistanceDiag, InputMode.BotsPosition])
            )

        # Create game engine
        gameEngine = GameEngine(bots_list, debug=False)

        # Run the game
        turn_number = 0
        bot_score_live_duration = [0 for i in bots_list]
        while True:
            gameEngine.next_turn()
            if gameEngine.is_finished():
                # print("Game finished at turn: " + str(turn_number))
                bot_score_live_duration = gameEngine.bot_live_duration
                # print("Bot score: ", bot_score_live_duration)
                break
            turn_number += 1

        # Give the winner a boost in score
        winners = [i for i, x in enumerate(bot_score_live_duration) if x == max(bot_score_live_duration)]
        for winner in winners:
            bot_score_live_duration[winner] += 50

        return bot_score_live_duration

    def selection(self, fitness_population, number_parents, index_best):
        index_best_parents = index_best[-number_parents:]
        return self.population[index_best_parents, :]

    def crossover(self, parents, offspring_size):
        offspring = np.empty(offspring_size)
        crossover_point = np.uint8(offspring_size[1] / 2)
        for k in range(offspring_size[0]):
            parent1_idx = k % parents.shape[0]
            parent2_idx = (k + 1) % parents.shape[0]
            offspring[k, 0:crossover_point] = parents[parent1_idx, 0:crossover_point]
            offspring[k, crossover_point:] = parents[parent2_idx, crossover_point:]
        return offspring

    def mutate(self, offspring):
        return offspring + np.random.uniform(-self.mutation_factor, self.mutation_factor, offspring.shape)
