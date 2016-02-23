from random import randrange, random


class Genotype:
    def __init__(self, length=1, initial_config=False, dna_vector=[], symbol_set_size=2):
        self.symbol_set_size = symbol_set_size
        self.legal_values = range(symbol_set_size)
        if initial_config:
            self.dna_vector = self.generate_random_dna_vector(length, symbol_set_size)
        else:
            self.dna_vector = dna_vector

    @staticmethod
    def generate_random_dna_vector(length, symbol_set_size):
        return [randrange(symbol_set_size) for _ in range(length)]

    def mutate(self, mutation_rate, mutation_protocol):
        if mutation_protocol == 1:
            #  Invividual
            r = random()
            if r <= mutation_rate:
                r_i = randrange(len(self.dna_vector))
                old_val = self.dna_vector[r_i]
                new_val = randrange(self.symbol_set_size - 1)
                if new_val >= old_val:
                    new_val += 1
                self.dna_vector[r_i] = new_val
        elif mutation_protocol == 2:
            #  Component
            for i in range(len(self.dna_vector)):
                r = random()
                if r <= mutation_rate:
                    old_val = self.dna_vector[i]
                    new_val = randrange(self.symbol_set_size - 1)
                    if new_val >= old_val:
                        new_val += 1
                    self.dna_vector[i] = new_val
