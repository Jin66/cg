import statistics

import numpy as np


class BasicGeneticAlgorithm:
    population_size = 50
    uniform_params = 4
    number_parents = 20
    number_offspring = 20
    mutation_factor = 1

    def __init__(self, number_generation, fitness_function, population=None, genes_size=48):
        self.genes_size = genes_size
        self.fitness_function = fitness_function
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
        results = {"fitness_mean": [], "fitness_best": []}
        fitness_population = []
        for generation in range(self.number_generation):
            print("Generation:", generation)

            # Compute population fitness
            fitness_population = self.fitness_function.compute(self.population)
            print("Fitness: ", fitness_population)
            print("Mean fitness: ", statistics.mean(fitness_population))
            results["fitness_mean"].append(statistics.mean(fitness_population))
            sort_fitness = np.argsort(fitness_population)
            print("Best fitness:", fitness_population[sort_fitness[-1]])
            results["fitness_best"].append(fitness_population[sort_fitness[-1]])
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
        results["best_individual"] = self.population[index_best_parent]
        results["population"] = self.population
        return results

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
