from __future__ import division
from random import random, choice
from copy import copy
from numpy import array, std

from genotype import Genotype
from phenotype import PhenotypeOneMax, PhenotypeLolzPrefix, PhenotypeSurprisingSequence


class Population:
    def __init__(self):
        self.genotype_pool = []
        self.phenotype_children_pool = []
        self.phenotype_adult_pool = []
        self.avg_fitness = 0.0

    def set_parameters(self, genotype_pool_size, adult_pool_size,
                       genotype_length, phenotype_length, adult_selection_protocol,
                       parent_selection_protocol, crossover_rate, points_of_crossover,
                       mutation_rate, mutation_protocol, zero_threshold, symbol_set_size,
                       target_surprising_sequence_length, tournament_size, tournament_slip_through_probability, problem):
        self.genotype_pool_size = genotype_pool_size
        self.adult_pool_size = adult_pool_size
        self.genotype_length = genotype_length
        self.phenotype_length = phenotype_length
        self.adult_selection_protocol = adult_selection_protocol
        self.parent_selection_protocol = parent_selection_protocol
        self.crossover_rate = crossover_rate
        self.points_of_crossover = points_of_crossover
        self.mutation_rate = mutation_rate
        self.mutation_protocol = mutation_protocol
        self.zero_threshold = zero_threshold
        self.symbol_set_size = symbol_set_size
        self.target_surprising_sequence_length = target_surprising_sequence_length
        self.tournament_size = tournament_size
        self.tournament_slip_through_probability = tournament_slip_through_probability
        self.problem = problem

    def initialize_genotypes(self):
        self.genotype_pool = [Genotype(self.genotype_length, initial_config=True) for _ in range(self.genotype_pool_size)]

    def develop_all_genotypes_to_phenotypes(self):
        self.phenotype_children_pool = []
        for genotype in self.genotype_pool:
            self.phenotype_children_pool.append(self.init_phenotype_type(genotype))

    def init_phenotype_type(self, genotype):
        if self.problem == 1:
            return PhenotypeOneMax(genotype)
        elif self.problem == 2:
            return PhenotypeLolzPrefix(genotype, zero_threshold=self.zero_threshold)
        elif self.problem == 3:
            return PhenotypeSurprisingSequence(genotype, symbol_set_size=self.symbol_set_size, local=True,
                                               target_surprising_sequence_length=self.target_surprising_sequence_length)
        elif self.problem == 4:
            return PhenotypeSurprisingSequence(genotype, symbol_set_size=self.symbol_set_size,
                                               target_surprising_sequence_length=self.target_surprising_sequence_length)

    def do_fitness_testing(self):
        for phenotype in self.phenotype_children_pool:
            phenotype.update_fitness_value()

    def refill_adult_pool(self):
        # Full And over-production. Dependant on difference between adult pool- and genotype pool size
        if self.adult_selection_protocol == 1:
            self.phenotype_children_pool.sort(reverse=True)
            self.phenotype_adult_pool = self.phenotype_children_pool[0:self.adult_pool_size]
        elif self.adult_selection_protocol == 3:  # mixing:
            self.phenotype_adult_pool = sorted((self.phenotype_children_pool + self.phenotype_adult_pool), reverse=True)[0:self.adult_pool_size]

    def scale_fitness_of_adult_pool(self):
        # TODO This array can be generated when calculating fitness
        fitness_array = array([phenotype.fitness_value for phenotype in self.phenotype_adult_pool], dtype=float)
        total_sum = sum(fitness_array)
        self.avg_fitness = total_sum/self.adult_pool_size
        self.standard_deviation = std(fitness_array)
        if self.parent_selection_protocol == 1:  # Fitness Proportionate
            self.scale_parents_fitness_proportionate(total_sum)
        elif self.parent_selection_protocol == 2:  # Sigma-scaling
            self.scale_parents_sigma_scaling()

    def select_parents_and_fill_genome_pool(self):
        self.scale_fitness_of_adult_pool()
        self.genotype_pool = []
        for _ in range(self.genotype_pool_size//2):
            if self.parent_selection_protocol == 1 or self.parent_selection_protocol == 2:  # Fitness Proportionate or Sigma-scaling using "roulette selection"
                parent1, parent2 = self.chose_parents_roulette()
            elif self.parent_selection_protocol == 3:  # Tournament Selection
                parent1, parent2 = self.chose_parents_tournament_selection()
            elif self.parent_selection_protocol == 4:
                parent1, parent2 = self.chose_parents_4th_selection()
            child1, child2 = self.mate_parents(parent1, parent2)
            self.genotype_pool.append(child1)
            self.genotype_pool.append(child2)

    def scale_parents_fitness_proportionate(self, total_sum):
        for adult in self.phenotype_adult_pool:
            adult.fitness_value_scaled = adult.fitness_value/total_sum

    def scale_parents_sigma_scaling(self):
        scaled_sum = 0
        if self.standard_deviation < 0.000001:
            for adult1 in self.phenotype_adult_pool:
                adult1.fitness_value_scaled = 1 / self.adult_pool_size
        else:
            for adult in self.phenotype_adult_pool:
                exp_val = 1 + ((adult.fitness_value - self.avg_fitness) / (2 * self.standard_deviation))
                adult.fitness_value_scaled = adult.fitness_value * exp_val
                scaled_sum += adult.fitness_value_scaled
            for scaled_adult in self.phenotype_adult_pool:
                scaled_adult.fitness_value_scaled = scaled_adult.fitness_value_scaled / scaled_sum

    def chose_parents_roulette(self):
        parent1 = self.chose_random_scaled_parent()
        while True:
            parent2 = self.chose_random_scaled_parent()
            if parent1 != parent2:
                break
        return parent1, parent2

    def chose_parents_tournament_selection(self):
        tournament_1 = []
        tournament_2 = []
        while len(tournament_1) < self.tournament_size:
            candidate = choice(self.phenotype_adult_pool)
            if candidate not in tournament_1:
                tournament_1.append(candidate)
        while len(tournament_2) < self.tournament_size:
            candidate = choice(self.phenotype_adult_pool)
            if candidate not in tournament_1 and candidate not in tournament_2:
                tournament_2.append(candidate)
        tournament_1.sort(reverse=True)
        tournament_2.sort(reverse=True)
        r1 = random()
        if r1 > self.tournament_slip_through_probability:
            parent1 = tournament_1[0]
        else:
            parent1 = choice(tournament_1[1:])
        r2 = random()
        if r2 > self.tournament_slip_through_probability:
            parent2 = tournament_2[0]
        else:
            parent2 = choice(tournament_2[1:])
        return parent1, parent2


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
            child1 = Genotype(self.genotype_length, bit_vector=copy(parent1.parent.bit_vector))
            child2 = Genotype(self.genotype_length, bit_vector=copy(parent2.parent.bit_vector))
        child1.mutate(mutation_rate=self.mutation_rate, mutation_protocol=self.mutation_protocol)
        child2.mutate(mutation_rate=self.mutation_rate, mutation_protocol=self.mutation_protocol)
        return child1, child2

    def create_crossover_bit_vector(self, parent1, parent2):
        component_bulk_size = self.genotype_length//(self.points_of_crossover + 1)
        child1_bit_vector = []
        child2_bit_vector = []
        for i in range(self.points_of_crossover):
            if i % 2 == 0:
                child1_bit_vector += copy(parent1.parent.bit_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
                child2_bit_vector += copy(parent2.parent.bit_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
            else:
                child1_bit_vector += copy(parent2.parent.bit_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
                child2_bit_vector += copy(parent1.parent.bit_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
        if self.points_of_crossover % 2 == 0:
            child1_bit_vector += copy(parent1.parent.bit_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
            child2_bit_vector += copy(parent2.parent.bit_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
        else:
            child1_bit_vector += copy(parent2.parent.bit_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
            child2_bit_vector += copy(parent1.parent.bit_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
        return child1_bit_vector, child2_bit_vector
