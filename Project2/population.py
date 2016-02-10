from __future__ import division
from random import random
from copy import copy

from genotype import Genotype
from phenotype import PhenotypeOneMax


class Population:
    def __init__(self):
        self.genotype_pool = []
        self.phenotype_children_pool = []
        self.phenotype_adult_pool = []
        self.avg_fitness = 0.0

    def set_parameters(self, genotype_pool_size, adult_pool_size,
                       genotype_length, phenotype_length, adult_selection_protocol,
                       parent_selection_protocol, crossover_rate, points_of_crossover,
                       mutation_rate_individual, mutation_rate_component):
        self.genotype_pool_size = genotype_pool_size
        self.adult_pool_size = adult_pool_size
        self.genotype_length = genotype_length
        self.phenotype_length = phenotype_length
        self.adult_selection_protocol = adult_selection_protocol
        self.parent_selection_protocol = parent_selection_protocol
        self.crossover_rate = crossover_rate
        self.points_of_crossover = points_of_crossover
        self.mutation_rate_individual = mutation_rate_individual
        self.mutation_rate_component = mutation_rate_component

    def initialize_genotypes(self):
        self.genotype_pool = [Genotype(self.genotype_length, initial_config=True) for _ in range(self.genotype_pool_size)]

    def develop_all_genotypes_to_phenotypes(self):
        self.phenotype_children_pool = []
        for genotype in self.genotype_pool:
            self.phenotype_children_pool.append(self.develop_genotype_to_phenotype(genotype))

    def develop_genotype_to_phenotype(self, genotype):
        return PhenotypeOneMax(genotype.bit_vector)

    def do_fitness_testing(self):
        for phenotype in self.phenotype_children_pool:
            phenotype.update_fitness_value()

    def refill_adult_pool(self):
        if self.adult_selection_protocol == 1:  # Full
            self.phenotype_children_pool.sort(reverse=True)
            self.phenotype_adult_pool = self.phenotype_children_pool[0:self.adult_pool_size]
        elif self.adult_selection_protocol == 2:  # over-production
            raise NotImplementedError
        elif self.adult_selection_protocol == 3:  # mixing:
            self.phenotype_adult_pool = sorted((self.phenotype_children_pool + self.phenotype_adult_pool), reverse=True)[0:self.adult_pool_size]

    def scale_fitness_of_adult_pool(self):
        total_sum = sum([phenotype.fitness_value for phenotype in self.phenotype_adult_pool])
        self.avg_fitness = total_sum/self.adult_pool_size
        for adult in self.phenotype_adult_pool:
            adult.fitness_value_scaled = adult.fitness_value/total_sum

    def select_parents_and_fill_genome_pool(self):
        self.genotype_pool = []
        for _ in range(self.genotype_pool_size//2):
            if self.parent_selection_protocol == 1:  # Fitness Proportionate
                parent1, parent2 = self.chose_parents_fitness_proportionate()
            elif self.parent_selection_protocol == 2:  # Sigma-scaling
                parent1, parent2 = self.chose_parents_sigma_scaling()
            elif self.parent_selection_protocol == 3:  # Tournament Selection
                parent1, parent2 = self.chose_parents_tournament_selection()
            elif self.parent_selection_protocol == 4:
                parent1, parent2 = self.chose_parents_4th_selection()
            child1, child2 = self.mate_parents(parent1, parent2)
            self.genotype_pool.append(child1)
            self.genotype_pool.append(child2)

    def chose_parents_fitness_proportionate(self):
        parent1 = self.chose_random_scaled_parent()
        while True:
            parent2 = self.chose_random_scaled_parent()
            if parent1 != parent2:
                break
        return parent1, parent2

    def chose_parents_sigma_scaling(self):
        raise NotImplementedError

    def chose_parents_tournament_selection(self):
        raise NotImplementedError

    def chose_parents_4th_selection(self):
        raise NotImplementedError

    def chose_random_scaled_parent(self):
        r = random()
        piece = 0.0
        for adult in self.phenotype_adult_pool:
            piece += adult.fitness_value_scaled
            if r <= piece:
                return adult

    def mate_parents(self, parent1, parent2):
        r = random()
        if r <= self.crossover_rate:
            child1_bit_vector, child2_bit_vector = self.create_crossover_bit_vector(parent1, parent2)
            child1 = Genotype(self.genotype_length, bit_vector=child1_bit_vector)
            child2 = Genotype(self.genotype_length, bit_vector=child2_bit_vector)
        else:
            child1 = Genotype(self.genotype_length, bit_vector=copy(parent1.components))
            child2 = Genotype(self.genotype_length, bit_vector=copy(parent2.components))
        child1.mutate_individual(individual_mutation_rate=self.mutation_rate_individual)
        child2.mutate_individual(individual_mutation_rate=self.mutation_rate_individual)
        return child1, child2

    def create_crossover_bit_vector(self, parent1, parent2):
        component_bulk_size = self.genotype_length//(self.points_of_crossover + 1)
        child1_bit_vector = []
        child2_bit_vector = []
        for i in range(self.points_of_crossover):
            if i % 2 == 0:
                child1_bit_vector += copy(parent1.components[i * component_bulk_size:(i + 1) * component_bulk_size])
                child2_bit_vector += copy(parent2.components[i * component_bulk_size:(i + 1) * component_bulk_size])
            else:
                child1_bit_vector += copy(parent2.components[i * component_bulk_size:(i + 1) * component_bulk_size])
                child2_bit_vector += copy(parent1.components[i * component_bulk_size:(i + 1) * component_bulk_size])
        if self.points_of_crossover % 2 == 0:
            child1_bit_vector += copy(parent1.components[i * component_bulk_size:(i + 1) * component_bulk_size])
            child2_bit_vector += copy(parent2.components[i * component_bulk_size:(i + 1) * component_bulk_size])
        else:
            child1_bit_vector += copy(parent2.components[i * component_bulk_size:(i + 1) * component_bulk_size])
            child2_bit_vector += copy(parent1.components[i * component_bulk_size:(i + 1) * component_bulk_size])
        return child1_bit_vector, child2_bit_vector
