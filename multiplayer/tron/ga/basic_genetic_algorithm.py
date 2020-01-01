import random
import statistics
from typing import List

import numpy as np


class GAResult:

    def __init__(self, old_results=None):
        """
            Create new result object for ga.
            Can copy an old result object.
        """

        if old_results is None:
            self.population = []
            self.fitness_best = []
            self.fitness_mean = []
            self.best_individual = None
            self.random_successful = []
            self.offspring_successful = []
            self.old_parent = []
        else:
            self.population = old_results.population
            self.fitness_best = old_results.fitness_best
            self.fitness_mean = old_results.fitness_mean
            self.best_individual = old_results.best_individual
            self.random_successful = old_results.random_successful
            self.offspring_successful = old_results.offspring_successful
            self.old_parent = old_results.old_parent

    def print_stats_turn(self, turn):
        print("Turn ", turn, ": ", self.fitness_mean[turn], "/", self.fitness_best[turn],
              "(", self.old_parent[turn], self.offspring_successful[turn], self.random_successful[turn], ")")


class OffspringGroup:

    def __init__(self, size, mutation_factor_min, mutation_factor_max):
        self.mutation_factor_max = mutation_factor_max
        self.mutation_factor_min = mutation_factor_min
        self.size = size


class BasicGeneticAlgorithm:
    uniform_params = 4
    mutation_factor = 1

    def __init__(self, number_generation, fitness_function,
                 number_parents=40,
                 offspring_groups: List[OffspringGroup] = None,
                 number_random=0,
                 genes_groups=None,
                 ga_results: GAResult = None,
                 genes_size=48):
        self.number_parents = number_parents
        self.number_random = number_random
        self.offspring_groups = offspring_groups
        if offspring_groups is None:
            self.offspring_groups = [OffspringGroup(60, 0.8, 1.2)]

        # Compute population size based on previous information
        self.population_size = self.number_parents + self.number_random
        for offspring_group in self.offspring_groups:
            self.population_size += offspring_group.size

        self.genes_groups = genes_groups
        self.genes_size = genes_size

        self.fitness_function = fitness_function
        self.number_generation = number_generation

        if ga_results is None:
            print("Creating random population...")
            self.init_random_population()
            self.ga_result = GAResult()
        else:
            print("Using imported population...(", len(ga_results.population), ")")
            self.population = ga_results.population
            self.ga_result = GAResult(ga_results)

    def init_random_population(self):
        self.population = self.get_random_individuals(self.population_size)

    def get_random_individuals(self, size):
        return np.random.uniform(low=-self.uniform_params, high=self.uniform_params, size=(size, self.genes_size))

    def run(self):
        fitness_population = []
        for generation in range(self.number_generation):
            print("Generation:", len(self.ga_result.fitness_best) + 1)

            # Compute population fitness
            fitness_population = self.fitness_function.compute(self.population)

            # Compute fitness statistics
            mean = statistics.mean(fitness_population)
            self.ga_result.fitness_mean.append(mean)

            sort_fitness = np.argsort(fitness_population)
            old_parent = 0
            offspring_successful = [0 for i in self.offspring_groups]
            random_successful = 0
            for idx in sort_fitness[-1:-self.number_parents:-1]:
                if idx < self.number_parents:
                    old_parent += 1
                    continue
                limit = self.number_parents
                group_id = 0
                found_offspring = False
                for off_group in self.offspring_groups:
                    if idx < limit + off_group.size:
                        offspring_successful[group_id] += 1
                        found_offspring = True
                        break
                    group_id += 1
                    limit = limit + off_group.size
                if not found_offspring:
                    random_successful += 1
            self.ga_result.old_parent.append(old_parent)
            self.ga_result.offspring_successful.append(offspring_successful)
            self.ga_result.random_successful.append(random_successful)
            self.ga_result.fitness_best.append(fitness_population[sort_fitness[-1]])
            self.ga_result.print_stats_turn(len(self.ga_result.fitness_best) - 1)

            # Generate new population
            # Parent
            parents = self.selection(self.number_parents, sort_fitness)
            self.population[0:self.number_parents, :] = parents

            # Offspring
            limit = self.number_parents
            for offspring_group in self.offspring_groups:
                offspring = self.crossover(parents, (offspring_group.size, self.genes_size))
                self.mutate(offspring, offspring_group.mutation_factor_min, offspring_group.mutation_factor_max)
                self.population[limit:limit + offspring_group.size, :] = offspring
                limit += + offspring_group.size

            # Random
            self.population[limit:, :] = self.get_random_individuals(self.number_random)

        index_best_parent = np.argsort(fitness_population)[-1]
        self.ga_result.best_individual = self.population[index_best_parent]
        self.ga_result.population = self.population
        return self.ga_result

    def selection(self, number_parents, index_best):
        index_best_parents = index_best[-number_parents:]
        return self.population[index_best_parents, :]

    def crossover(self, parents, offspring_size):
        offspring = np.empty(offspring_size)

        if self.genes_groups is None:
            # Simple crossover, separating genes into 2 equal parts
            crossover_point = np.uint8(offspring_size[1] / 2)
            for idx_offspring in range(offspring_size[0]):
                parent1_idx = idx_offspring % parents.shape[0]
                parent2_idx = (idx_offspring + 1) % parents.shape[0]
                offspring[idx_offspring, 0:crossover_point] = parents[parent1_idx, 0:crossover_point]
                offspring[idx_offspring, crossover_point:] = parents[parent2_idx, crossover_point:]
        else:
            # Crossover performed by grouping genes
            parent_idx = [0, 1]
            for idx_offspring in range(offspring_size[0]):
                parent_idx[0] = idx_offspring % parents.shape[0]
                parent_idx[1] = (idx_offspring + 1) % parents.shape[0]
                for idx_group in range(len(self.genes_groups)):
                    group = self.genes_groups[idx_group]
                    offspring[idx_offspring, group[0]:group[1]] = parents[parent_idx[idx_group % 2], group[0]:group[1]]
        return offspring

    def mutate(self, offspring, mutation_factor_min, mutation_factor_max):
        mutation_factor = random.uniform(mutation_factor_min, mutation_factor_max)
        if self.genes_groups is None:
            offspring = offspring + np.random.uniform(-mutation_factor, mutation_factor, offspring.shape)
        else:
            for idx_offspring in range(offspring.shape[0]):
                # Pick a group
                group_id = random.randrange(len(self.genes_groups))
                group = self.genes_groups[group_id]
                # Mutate
                mutation = np.random.uniform(-1, 1, (1, group[1] - group[0]))
                mutation /= np.linalg.norm(mutation)
                mutation *= mutation_factor
                offspring[idx_offspring, group[0]:group[1]] = \
                    offspring[idx_offspring, group[0]:group[1]] + \
                    mutation
