from __future__ import division
import abc


class Phenotype(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def fitness_evaluation(self):
        return

    @abc.abstractmethod
    def __lt__(self, other):
        return


class PhenotypeOneMax(Phenotype):
    def __init__(self, components):
        self.components = components
        self.fitness_value = None
        self.fitness_value_scaled = None

    def update_fitness_value(self):
        self.fitness_value = self.fitness_evaluation()

    def fitness_evaluation(self):
        return sum(self.components)/len(self.components)

    def __lt__(self, other):
        if self.fitness_value < other.fitness_value:
            return True
        return False
