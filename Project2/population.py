from __future__ import division
from random import random
from copy import copy

from genotype import Genotype
from phenotype import PhenotypeOneMax

GENOTYPE_POOL_SIZE = 10
ADULT_POOL_SIZE = 6
GENOTYPE_LENGTH = 50
PHENOTYPE_LENGTH = 50
DISCARD_OLD_ADULTS = False
GLOBAL_PARENT_COMPETITION = True


CROSSOVER_RATE = 0.2 # When two parents have a match, they have a X% chance of being recombined.
# When they are not combined they are simply copied (with mutations)
POINTS_OF_CROSSOVER = 3
MUTATION_RATE_INDIVIDUAL = 0.01 # X% av genomes are modified in ONE of their component
MUTATION_RATE_COMPONENT = 0.05 # Each component has a chance of mutating


class Population:
    def __init__(self):
        self.genotype_pool = self.initialize_genotypes()
        self.phenotype_children_pool = []
        self.phenotype_adult_pool = []

    def initialize_genotypes(self):
        return [Genotype(GENOTYPE_LENGTH, initial_config=True) for _ in range(GENOTYPE_POOL_SIZE)]

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
        if DISCARD_OLD_ADULTS:
            self.phenotype_children_pool.sort(reverse=True)
            self.phenotype_adult_pool = self.phenotype_children_pool[0:ADULT_POOL_SIZE]
        else:
            self.phenotype_adult_pool = sorted((self.phenotype_children_pool + self.phenotype_adult_pool), reverse=True)[0:ADULT_POOL_SIZE]

    def scale_fitness_of_adult_pool(self):
        total_sum = sum([phenotype.fitness_value for phenotype in self.phenotype_adult_pool])
        for adult in self.phenotype_adult_pool:
            adult.fitness_value_scaled = adult.fitness_value/total_sum

    def chose_parents_from_competition(self):
        if GLOBAL_PARENT_COMPETITION:
            parent1 = self.chose_random_scaled_parent()
            while True:
                parent2 = self.chose_random_scaled_parent()
                if parent1 != parent2:
                    break
            return parent1, parent2
        else:
            # TODO implement tournaments
            raise NotImplementedError

    def chose_random_scaled_parent(self):
        r = random()
        piece = 0.0
        for adult in self.phenotype_adult_pool:
            piece += adult.fitness_value_scaled
            if r <= piece:
                return adult

    def select_parents_and_fill_genome_pool(self):
        self.genotype_pool = []
        for _ in range(GENOTYPE_POOL_SIZE//2):
            parent1, parent2 = self.chose_parents_from_competition()
            child1, child2 = self.mate_parents(parent1, parent2)
            self.genotype_pool.append(child1)
            self.genotype_pool.append(child2)

    def mate_parents(self, parent1, parent2):
        r = random()
        if r <= CROSSOVER_RATE:
            child1_bit_vector, child2_bit_vector = self.create_crossover_bit_vector(parent1, parent2)
            child1 = Genotype(GENOTYPE_LENGTH, bit_vector=child1_bit_vector)
            child2 = Genotype(GENOTYPE_LENGTH, bit_vector=child2_bit_vector)
        else:
            child1 = Genotype(GENOTYPE_LENGTH, bit_vector=parent1.components)
            child2 = Genotype(GENOTYPE_LENGTH, bit_vector=parent2.components)
        child1.mutate_individual(individual_mutation_rate=MUTATION_RATE_INDIVIDUAL)
        child2.mutate_individual(individual_mutation_rate=MUTATION_RATE_INDIVIDUAL)
        return child1, child2

    def create_crossover_bit_vector(self, parent1, parent2):
        component_bulk_size = GENOTYPE_LENGTH//(POINTS_OF_CROSSOVER + 1)
        child1_bit_vector = []
        child2_bit_vector = []
        for i in range(POINTS_OF_CROSSOVER):
            if i % 2 == 0:
                child1_bit_vector += copy(parent1.components[i * component_bulk_size:(i + 1) * component_bulk_size])
                child2_bit_vector += copy(parent2.components[i * component_bulk_size:(i + 1) * component_bulk_size])
            else:
                child1_bit_vector += copy(parent2.components[i * component_bulk_size:(i + 1) * component_bulk_size])
                child2_bit_vector += copy(parent1.components[i * component_bulk_size:(i + 1) * component_bulk_size])
        if POINTS_OF_CROSSOVER % 2 == 0:
            child1_bit_vector += copy(parent1.components[i * component_bulk_size:(i + 1) * component_bulk_size])
            child2_bit_vector += copy(parent2.components[i * component_bulk_size:(i + 1) * component_bulk_size])
        else:
            child1_bit_vector += copy(parent2.components[i * component_bulk_size:(i + 1) * component_bulk_size])
            child2_bit_vector += copy(parent1.components[i * component_bulk_size:(i + 1) * component_bulk_size])
        return child1_bit_vector, child2_bit_vector
