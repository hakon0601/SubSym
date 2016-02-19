from __future__ import division
from math import log, ceil
from collections import defaultdict


class Phenotype:
    def __init__(self):
        self.fitness_value = None
        self.fitness_value_scaled = None

    def develop_from_genotype(self, genotype):
        return NotImplementedError

    def update_fitness_value(self):
        self.fitness_value = self.fitness_evaluation()

    def fitness_evaluation(self):
        raise NotImplementedError

    def __lt__(self, other):
        if self.fitness_value < other.fitness_value:
            return True
        return False


class PhenotypeOneMax(Phenotype):
    def __init__(self, genotype):
        Phenotype.__init__(self)
        self.parent = None
        self.components = self.develop_from_genotype(genotype)

    def develop_from_genotype(self, genotype):
        self.parent = genotype
        return genotype.bit_vector

    def fitness_evaluation(self):
        return sum(self.components)/len(self.components)


class PhenotypeLolzPrefix(Phenotype):
    def __init__(self, genotype, zero_threshold=4):
        Phenotype.__init__(self)
        self.parent = None
        self.components = self.develop_from_genotype(genotype)
        self.zero_threshold = zero_threshold

    def develop_from_genotype(self, genotype):
        self.parent = genotype
        return genotype.bit_vector

    def fitness_evaluation(self):
        first_value = self.components[0]
        for i in range(1, len(self.components)):
            if self.components[i] != first_value or (first_value == 0 and (i + 1) == (self.zero_threshold + 1)):
                return i/len(self.components)
        return 1.0


class PhenotypeSurprisingSequence(Phenotype):
    def __init__(self, genotype, symbol_set_size, local=False, target_surprising_sequence_length=5):
        Phenotype.__init__(self)
        self.local = local
        self.target_surprising_sequence_length = target_surprising_sequence_length
        self.symbol_set_size = symbol_set_size
        self.parent = None
        self.bit_to_symbol_rate = int(ceil(log(self.symbol_set_size, 2)))
        self.longest_surprising_sequence = []
        self.components = self.develop_from_genotype(genotype)

    def develop_from_genotype(self, genotype):
        self.parent = genotype
        components = []
        for i in range(0, (len(genotype.bit_vector)//self.bit_to_symbol_rate)*self.bit_to_symbol_rate , self.bit_to_symbol_rate):
            sym_nr = 0
            for bit in genotype.bit_vector[i:i + self.bit_to_symbol_rate]:
                sym_nr = (sym_nr << 1) | bit
            if sym_nr < self.symbol_set_size:
                components.append(sym_nr)
            #else:
            #    components.append(-1)
        return components


    def fitness_evaluation(self):
        longest_surprising_sequence = []
        for i in range(len(self.components) + 1 - 3):
            for j in range(i + 3, len(self.components) + 1):
                if self.check_components_for_unsurprising_sequence(self.components[i:j]):
                    if (j - i) > len(longest_surprising_sequence):
                        longest_surprising_sequence = self.components[i:j]
                else:
                    break
        self.longest_surprising_sequence = longest_surprising_sequence
        fitness = len(longest_surprising_sequence) / self.target_surprising_sequence_length
        return fitness

    def check_components_for_unsurprising_sequence(self, components):
        frequence_dict = defaultdict(int)
        for i in range(len(components) - 1):
            for j in range(i + 1, len(components)):
                if frequence_dict[(components[i],(j - i), components[j])] == 0:
                    frequence_dict[(components[i],(j - i), components[j])] += 1
                else:
                    return False
                if self.local:
                    break
        return True
