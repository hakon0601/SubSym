from random import randrange, random
from copy import copy


class Genotype:
    def __init__(self, length=1, initial_config=False, dna_vector=[], symbol_set_size=2):
        self.symbol_set_size = symbol_set_size
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

    def create_crossover_dna_vector(self, other, points_of_crossover=1, fixed_points=False):
        if not fixed_points:
            crossover_points = []
            while len(crossover_points) < points_of_crossover:
                candidate_point = randrange(1, len(self.dna_vector))
                if candidate_point not in crossover_points:
                    crossover_points.append(candidate_point)
            crossover_points.sort()
            crossover_points.append(len(self.dna_vector))
            child1_dna_vector = []
            child2_dna_vector = []
            last_point = 0
            for i in range(len(crossover_points)):
                point = crossover_points[i]
                if i % 2 == 0:
                    child1_dna_vector += copy(self.dna_vector[last_point:point])
                    child2_dna_vector += copy(other.dna_vector[last_point:point])
                else:
                    child1_dna_vector += copy(other.dna_vector[last_point:point])
                    child2_dna_vector += copy(self.dna_vector[last_point:point])
                last_point = point
        else:
            component_bulk_size = len(self.dna_vector) // (points_of_crossover + 1)
            child1_dna_vector = []
            child2_dna_vector = []
            for i in range(points_of_crossover):
                if i % 2 == 0:
                    child1_dna_vector += copy(self.dna_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
                    child2_dna_vector += copy(other.dna_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
                else:
                    child1_dna_vector += copy(other.dna_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
                    child2_dna_vector += copy(self.dna_vector[i * component_bulk_size:(i + 1) * component_bulk_size])
            if points_of_crossover % 2 == 0:
                child1_dna_vector += copy(self.dna_vector[(i + 1) * component_bulk_size:])
                child2_dna_vector += copy(other.dna_vector[(i + 1) * component_bulk_size:])
            else:
                child1_dna_vector += copy(other.dna_vector[(i + 1) * component_bulk_size:])
                child2_dna_vector += copy(self.dna_vector[(i + 1) * component_bulk_size:])
        return child1_dna_vector, child2_dna_vector

# a = Genotype(length=5, dna_vector=[0, 1, 2, 3, 4, 5], symbol_set_size=10)
# b = Genotype(length=5, dna_vector=[6, 7, 8, 9, 10, 11], symbol_set_size=10)
# print a.dna_vector
# print b.dna_vector
# print a.create_crossover_dna_vector(b, points_of_crossover=2, fixed_points=True)
