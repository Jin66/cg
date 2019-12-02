import statistics

import numpy as np


class GAResult:

    def __init__(self, ga_result=None):
        """
            Create new result object for ga.
            Can copy an old result object.
        """
        if ga_result is None:
            self.population = []
            self.fitness_best = []
            self.fitness_mean = []
            self.best_individual = None
        else:
            self.population = ga_result.population
            self.fitness_best = ga_result.fitness_best
            self.fitness_mean = ga_result.fitness_mean
            self.best_individual = ga_result.best_individual


class BasicGeneticAlgorithm:
    population_size = 50
    uniform_params = 4
    number_parents = 20
    number_offspring = 20
    mutation_factor = 1

    def __init__(self, number_generation, fitness_function, genes_groups=None, ga_results: GAResult = None,
                 genes_size=48):
        self.genes_groups = genes_groups
        self.genes_size = genes_size
        self.fitness_function = fitness_function
        self.number_generation = number_generation

        if ga_results is None:
            print("Creating random population...")
            self.init_population(self.population_size)
            self.ga_result = GAResult()
        else:
            print("Using imported population...(", len(ga_results.population), ")")
            self.population = ga_results.population
            self.ga_result = GAResult(ga_results)

    def init_population(self, population_size):
        self.population = self.get_random_individuals(self.population_size)

    def get_random_individuals(self, size):
        return np.random.uniform(low=-self.uniform_params, high=self.uniform_params, size=(size, self.genes_size))

    def run(self):
        fitness_population = []
        for generation in range(self.number_generation):
            print("Generation:", generation)

            # Compute population fitness
            fitness_population = self.fitness_function.compute(self.population)
            print("Fitness: ", fitness_population)
            print("Mean fitness: ", statistics.mean(fitness_population))
            self.ga_result.fitness_mean.append(statistics.mean(fitness_population))
            sort_fitness = np.argsort(fitness_population)
            print("Best fitness:", fitness_population[sort_fitness[-1]])
            self.ga_result.fitness_best.append(fitness_population[sort_fitness[-1]])
            print(self.population[sort_fitness[-1]])

            # Generate new population
            parents = self.selection(fitness_population, self.number_parents, sort_fitness)
            offspring = self.crossover(parents, (self.number_offspring, self.genes_size))
            mutated_offspring = self.mutate(offspring)
            self.population[0:self.number_parents, :] = parents
            self.population[self.number_parents:self.number_parents + self.number_offspring, :] = mutated_offspring
            filing_size = self.population_size - (self.number_parents + self.number_offspring)
            self.population[self.number_parents + self.number_offspring:, :] = self.get_random_individuals(filing_size)

        index_best_parent = np.argsort(fitness_population)[-1]
        self.ga_result.best_individual = self.population[index_best_parent]
        self.ga_result.population = self.population
        return self.ga_result

    def selection(self, fitness_population, number_parents, index_best):
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

    def mutate(self, offspring):
        return offspring + np.random.uniform(-self.mutation_factor, self.mutation_factor, offspring.shape)
