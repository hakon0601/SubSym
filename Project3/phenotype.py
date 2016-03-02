from __future__ import division
from random import random
from copy import deepcopy
from direction import Direction
from cell_item import CellItem
from ann import Ann


class Phenotype:
    def __init__(self, genotype):
        self.fitness_value = None
        self.fitness_value_scaled = None
        self.parent = genotype

    def develop_from_genotype(self):
        return NotImplementedError

    def update_fitness_value(self):
        self.fitness_value = self.fitness_evaluation()

    def fitness_evaluation(self):
        raise NotImplementedError

    def __lt__(self, other):
        if self.fitness_value < other.fitness_value:
            return True
        elif self.fitness_value > other.fitness_value:
            return False
        else:
            r = random()
            if r >= 0.5:
                return True
            return False


class PhenotypeAnn(Phenotype):
    def __init__(self, genotype, hidden_layers, activation_functions):
        Phenotype.__init__(self, genotype)
        self.components = self.develop_from_genotype()
        self.hidden_layers = hidden_layers
        self.activation_functions = activation_functions

    def develop_from_genotype(self):
        return self.parent.dna_vector

    def fitness_evaluation(self, environments=None):
        environments_copy = deepcopy(environments)
        self.run_simulation(environments_copy)
        # Calculate the average score
        fitness_sum = 0
        for i in range(len(environments_copy)):
            fitness_sum += (environments_copy[i].agent.food_eaten + (environments_copy[i].poison_count - environments_copy[i].agent.poison_eaten)) / \
                           (environments_copy[i].food_count + environments_copy[i].poison_count)
        return fitness_sum / len(environments_copy)

    # Testing the phenotype configuration on the environments
    def run_simulation(self, environments_copy):
        weights = self.prepare_weights_for_ann()
        ann = Ann(weights=weights, hidden_layers=self.hidden_layers, activation_functions=self.activation_functions)
        for j in range(len(environments_copy)):
            environment = environments_copy[j]
            agent = environments_copy[j].agent
            for k in range(60):
                agent_sensor_output = agent.sense_front_left_right(environment)
                ann_inputs = [1 if agent_sensor_output[0] == CellItem.food else 0,
                              1 if agent_sensor_output[1] == CellItem.food else 0,
                              1 if agent_sensor_output[2] == CellItem.food else 0,
                              1 if agent_sensor_output[0] == CellItem.poison else 0,
                              1 if agent_sensor_output[1] == CellItem.poison else 0,
                              1 if agent_sensor_output[2] == CellItem.poison else 0]
                prediction = ann.predict(inputs=ann_inputs)
                best_index = prediction.argmax()
                if best_index == 1:
                    agent.move_left()
                elif best_index == 2:
                    agent.move_right()
                agent.move_forward(environment)

    def prepare_weights_for_ann(self):
        weights = []
        last_component_index = 0
        for k in range(len(self.hidden_layers) - 1):
            weights.append([])
            for i in range(self.hidden_layers[k]):
                weights[k].append(self.components[
                                  last_component_index + i * self.hidden_layers[k + 1]:
                                  last_component_index + (i + 1)*self.hidden_layers[k + 1]])
            last_component_index = last_component_index + self.hidden_layers[k] * self.hidden_layers[k + 1]
        return weights
