from __future__ import division
from random import random, choice
from copy import copy, deepcopy
from numpy import array, std
from math import exp
from genotype import Genotype
from phenotype import PhenotypeAnn
from multi import *


class EvolutionaryAlgorithm:
    def __init__(self, genotype_pool_size, adult_pool_size, elitism,
                 genotype_length, phenotype_length, adult_selection_protocol,
                 parent_selection_protocol, crossover_rate, points_of_crossover,
                 mutation_rate, mutation_protocol, symbol_set_size,
                 tournament_size, tournament_slip_through_probability, initial_temperature,
                 hidden_layers, activation_functions, generations):
        self.genotype_pool = []
        self.phenotype_children_pool = []
        self.phenotype_adult_pool = []
        self.avg_fitness = 0.0
        self.standard_deviation = 0.0
        self.genotype_pool_size = genotype_pool_size
        self.adult_pool_size = adult_pool_size
        self.elitism = elitism
        self.genotype_length = genotype_length
        self.phenotype_length = phenotype_length
        self.adult_selection_protocol = adult_selection_protocol
        self.parent_selection_protocol = parent_selection_protocol
        self.crossover_rate = crossover_rate
        self.points_of_crossover = points_of_crossover
        self.mutation_rate = mutation_rate
        self.mutation_protocol = mutation_protocol
        self.symbol_set_size = symbol_set_size
        self.tournament_size = tournament_size
        self.tournament_slip_through_probability = tournament_slip_through_probability
        self.temperature = initial_temperature
        self.temperature_step = initial_temperature / generations
        self.generations = generations
        self.activation_functions = activation_functions
        self.hidden_layers = hidden_layers

        self.initialize_genotypes()

    def initialize_genotypes(self):
        self.genotype_pool = [Genotype(length=self.genotype_length,
                                       initial_config=True,
                                       symbol_set_size=self.symbol_set_size)
                              for _ in range(self.genotype_pool_size)]

    def run_one_life_cycle(self, environments):
        # Evolve phenotypes from the pool of genotypes
        self.develop_all_genotypes_to_phenotypes()
        # Calculate fitness of adults
        self.do_fitness_testing(environments)
        self.refill_adult_pool()
        self.select_parents_and_fill_genome_pool()

    def develop_all_genotypes_to_phenotypes(self):
        self.phenotype_children_pool = []
        for genotype in self.genotype_pool:
            # The actual development happens under initialization of a new phenotype using a genotypes dna
            self.phenotype_children_pool.append(self.init_phenotype_type(genotype))

    def init_phenotype_type(self, genotype):
        return PhenotypeAnn(genotype,
                            symbol_set_size=self.symbol_set_size,
                            hidden_layers=self.hidden_layers,
                            activation_functions=self.activation_functions)

    def do_fitness_testing(self, environments):
        PhenotypeAnn.environments_for_fitness = environments
        res = parmap(PhenotypeAnn.fitness_evaluation, self.phenotype_children_pool)
        for i in range(len(res)):
            self.phenotype_children_pool[i].fitness_value = res[i]

        if self.adult_selection_protocol == 3:
            res = parmap(PhenotypeAnn.fitness_evaluation, self.phenotype_adult_pool)
            for i in range(len(res)):
                self.phenotype_adult_pool[i].fitness_value = res[i]

    def refill_adult_pool(self):
        # Full And over-production. Dependant on difference between adult pool- and genotype pool size
        if self.adult_selection_protocol == 1 or self.adult_selection_protocol == 2:
            self.phenotype_adult_pool = sorted(self.phenotype_children_pool, reverse=True)
        elif self.adult_selection_protocol == 3:  # mixing:
            self.phenotype_adult_pool = sorted(list(self.phenotype_children_pool + self.phenotype_adult_pool),
                                               reverse=True)
        self.phenotype_adult_pool = self.phenotype_adult_pool[:self.adult_pool_size]

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
        elif self.parent_selection_protocol == 4:  # Boltzmann-scaling
            self.scale_parents_boltzmann(total_sum)

    def select_parents_and_fill_genome_pool(self):
        self.scale_fitness_of_adult_pool()
        self.genotype_pool = []
        self.add_elite_children()
        for _ in range((self.genotype_pool_size - self.elitism)//2):
            # Fitness Proportionate or Sigma-scaling or boltzmann using "roulette selection"
            if self.parent_selection_protocol == 1 or \
                            self.parent_selection_protocol == 2 or \
                            self.parent_selection_protocol == 4:
                parent1, parent2 = self.chose_parents_roulette()
            elif self.parent_selection_protocol == 3:  # Tournament Selection
                parent1, parent2 = self.chose_parents_tournament_selection()
            child1, child2 = self.mate_parents(parent1, parent2)
            self.genotype_pool.append(child1)
            self.genotype_pool.append(child2)

    def add_elite_children(self):
        for i in range(self.elitism):
            self.genotype_pool.append(Genotype(
                    self.genotype_length,
                    dna_vector=copy(self.phenotype_adult_pool[i].parent.dna_vector),
                    symbol_set_size=self.symbol_set_size))

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

    def scale_parents_boltzmann(self, total_sum):
        exp_sum = 0
        for parent in self.phenotype_adult_pool:
            parent.fitness_value_scaled = exp(parent.fitness_value / self.temperature)
            exp_sum += parent.fitness_value_scaled
        avg = exp_sum / self.adult_pool_size
        for parent2 in self.phenotype_adult_pool:
            exp_val = (parent2.fitness_value_scaled / avg)
            parent2.fitness_value_scaled = (exp_val * parent2.fitness_value)/total_sum
        self.temperature -= self.temperature_step

    def chose_parents_roulette(self):
        parent1 = self.chose_random_scaled_parent()
        while True:
            parent2 = self.chose_random_scaled_parent()
            if parent1 is not parent2:
                break
        return parent1, parent2

    def chose_parents_tournament_selection(self):
        tournament_1 = []
        selection_pool = deepcopy(self.phenotype_adult_pool)
        while len(tournament_1) < self.tournament_size:
            candidate = choice(selection_pool)
            selection_pool.remove(candidate)
            tournament_1.append(candidate)
        tournament_1.sort(reverse=True)
        r1 = random()
        if r1 > self.tournament_slip_through_probability:
            parent1 = tournament_1[0]
        else:
            parent1 = choice(tournament_1[1:])
        tournament_1.remove(parent1)
        r2 = random()
        if r2 > self.tournament_slip_through_probability:
            parent2 = tournament_1[0]
        else:
            parent2 = choice(tournament_1[1:])
        return parent1, parent2

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
            child1_dna_vector, child2_dna_vector = parent1.parent.create_crossover_dna_vector(parent2.parent,
                                                                                              self.points_of_crossover)
            child1 = Genotype(self.genotype_length, dna_vector=copy(child1_dna_vector),
                              symbol_set_size=self.symbol_set_size)
            child2 = Genotype(self.genotype_length, dna_vector=copy(child2_dna_vector),
                              symbol_set_size=self.symbol_set_size)
        else:
            child1 = Genotype(self.genotype_length, dna_vector=copy(parent1.parent.dna_vector),
                              symbol_set_size=self.symbol_set_size)
            child2 = Genotype(self.genotype_length, dna_vector=copy(parent2.parent.dna_vector),
                              symbol_set_size=self.symbol_set_size)
        child1.mutate(mutation_rate=self.mutation_rate, mutation_protocol=self.mutation_protocol)
        child2.mutate(mutation_rate=self.mutation_rate, mutation_protocol=self.mutation_protocol)
        return child1, child2
