from __future__ import division


class Phenotype:
    def __init__(self, components):
        self.components = components
        self.fitness_value = None
        self.fitness_value_scaled = None

    def fitness_evaluation(self):
        return 1

    def __lt__(self, other):
        if self.fitness_value < other.fitness_value:
            return True
        return False


class PhenotypeOneMax(Phenotype):
    def __init__(self, components):
        Phenotype.__init__(self, components)

    def update_fitness_value(self):
        self.fitness_value = self.fitness_evaluation()

    def fitness_evaluation(self):
        return sum(self.components)/len(self.components)