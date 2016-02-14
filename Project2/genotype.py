from random import randint, random


class Genotype:
    def __init__(self, length=1, initial_config=False, bit_vector=[]):
        if initial_config:
            self.bit_vector = self.generate_random_bit_vector(length)
        else:
            self.bit_vector = bit_vector

    @staticmethod
    def generate_random_bit_vector(length):
        return [randint(0, 1) for _ in range(length)]

    def mutate(self, mutation_rate, mutation_protocol):
        if mutation_protocol == 1:
            #  Invividual
            r = random()
            if r <= mutation_rate:
                r_i = randint(0, len(self.bit_vector) - 1)
                self.bit_vector[r_i] = int(not self.bit_vector[r_i])
        elif mutation_protocol == 2:
            #  Component
            for i in range(len(self.bit_vector)):
                r = random()
                if r <= mutation_rate:
                    self.bit_vector[i] = int(not self.bit_vector[i])

    def mutate_component(self):
        raise NotImplementedError