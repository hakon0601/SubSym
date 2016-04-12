from __future__ import division
from random import random
from copy import deepcopy
from ctrann import Ann
from constants import *
from math import floor


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


class PhenotypeBeerTracker(Phenotype):

    environments_for_fitness = None

    def __init__(self, genotype, symbol_set_size, hidden_layers, activation_functions):
        Phenotype.__init__(self, genotype)
        self.symbol_set_size = symbol_set_size
        self.hidden_layers = hidden_layers
        self.nr_of_non_input_neuron = sum(self.hidden_layers[1:])
        self.components = self.develop_from_genotype()
        self.activation_functions = activation_functions

    def develop_from_genotype(self):
        # Regular weights
        components = [self.map_to_range(self.parent.dna_vector[i], 0, self.symbol_set_size - 1, WEIGHT_MIN, WEIGHT_MAX)
                for i in range(len(self.parent.dna_vector) - (3 * self.nr_of_non_input_neuron))]
        # Bias weights
        for j in range(self.nr_of_non_input_neuron):
            bias_index = i + 1 + j
            components.append(self.map_to_range(self.parent.dna_vector[bias_index],
                                                0, self.symbol_set_size - 1, BIAS_MIN, BIAS_MAX))
        # Gains
        for k in range(self.nr_of_non_input_neuron):
            gains_index = bias_index + 1 + k
            components.append(self.map_to_range(self.parent.dna_vector[gains_index],
                                                0, self.symbol_set_size - 1, GAINS_MIN, GAINS_MAX))
        # Time-constants
        for l in range(self.nr_of_non_input_neuron):
            time_constant_index = gains_index + 1 + l
            components.append(self.map_to_range(self.parent.dna_vector[time_constant_index],
                                                0, self.symbol_set_size - 1, TIME_CONSTANT_MIN, TIME_CONSTANT_MAX))
        return components

    @staticmethod
    def fitness_evaluation(phenotype):
        environments_copy = deepcopy(PhenotypeBeerTracker.environments_for_fitness)
        phenotype.run_simulation(environments_copy)
        # Calculate the average score
        fitness_sum = 0
        for i in range(len(environments_copy)):
            if environments_copy[i].agent.agent_type == 1:
                catching_fitness = environments_copy[i].score[0][0] / environments_copy[i].nr_of_small_objects
                #catching_fitness += (environments_copy[i].score[0][2] * 0.1) / environments_copy[i].nr_of_small_objects
                catching_fitness *= 0.6
                avoidance_fitness = environments_copy[i].score[1][1] / environments_copy[i].nr_of_large_objects
                #avoidance_fitness += (environments_copy[i].score[1][2] * 0.1) / environments_copy[i].nr_of_large_objects
                avoidance_fitness *= 0.4
                fitness_sum += catching_fitness + avoidance_fitness
            elif environments_copy[i].agent.agent_type == 2:
                catching_fitness = environments_copy[i].score[0][0] / environments_copy[i].nr_of_small_objects
                catching_fitness *= 0.9
                avoidance_fitness = environments_copy[i].score[1][1] / environments_copy[i].nr_of_large_objects
                avoidance_fitness *= 0.1
                fitness_sum += catching_fitness + avoidance_fitness
            else:
                # TODO make pull fitness
                pass
        return fitness_sum / len(environments_copy)

    # Testing the phenotype configuration on the environments
    def run_simulation(self, environments_copy):
        weights = self.prepare_weights_for_ann()
        ann = Ann(weights=weights, hidden_layers=self.hidden_layers, activation_functions=self.activation_functions,
                  gains=self.get_gains(), time_constants=self.get_time_constants())
        for j in range(len(environments_copy)):
            for _ in range(TIMESTEPS):
                environments_copy[j].drop_object_one_level()
                agent_sensor_output = environments_copy[j].agent.get_sensor_array(environments_copy[j])
                ann_inputs = agent_sensor_output
                prediction = ann.predict(inputs=ann_inputs)
                best_index = prediction.argmax()
                if ONE_HOT_OUTPUT:
                    if best_index == 0:
                        pass
                    elif best_index == 1:
                        environments_copy[j].agent.move_right(x_direction_size=1)
                    elif best_index == 2:
                        environments_copy[j].agent.move_right(x_direction_size=2)
                    elif best_index == 3:
                        environments_copy[j].agent.move_right(x_direction_size=3)
                    elif best_index == 4:
                        environments_copy[j].agent.move_right(x_direction_size=4)
                    elif best_index == 5:
                        environments_copy[j].agent.move_left(x_direction_size=1)
                    elif best_index == 6:
                        environments_copy[j].agent.move_left(x_direction_size=2)
                    elif best_index == 7:
                        environments_copy[j].agent.move_left(x_direction_size=3)
                    elif best_index == 8:
                        environments_copy[j].agent.move_left(x_direction_size=4)
                    elif environments_copy[j].agent.agent_type == 3 and best_index == 9:
                        environments_copy[j].pull_object()
                else:
                    if environments_copy[j].agent.agent_type == 3 and prediction[2] > PULL_THRESHOLD:
                        environments_copy[j].pull_object()
                    elif prediction[0] > 0.5:
                        # Move right
                        if prediction[1] < 0.2:
                            pass
                        elif prediction[1] < 0.4:
                            environments_copy[j].agent.move_right(x_direction_size=1)
                        elif prediction[1] < 0.6:
                            environments_copy[j].agent.move_right(x_direction_size=2)
                        elif prediction[1] < 0.8:
                            environments_copy[j].agent.move_right(x_direction_size=3)
                        else:
                            environments_copy[j].agent.move_right(x_direction_size=4)
                    else:
                        # Move left
                        if prediction[1] < 0.2:
                            pass
                        elif prediction[1] < 0.4:
                            environments_copy[j].agent.move_left(x_direction_size=1)
                        elif prediction[1] < 0.6:
                            environments_copy[j].agent.move_left(x_direction_size=2)
                        elif prediction[1] < 0.8:
                            environments_copy[j].agent.move_left(x_direction_size=3)
                        else:
                            environments_copy[j].agent.move_left(x_direction_size=4)
            environments_copy[j].set_nr_of_objects()

    def prepare_weights_for_ann(self):
        weights = []
        last_component_index = 0
        last_bias_component_index = len(self.components) - (3 * self.nr_of_non_input_neuron)
        for k in range(len(self.hidden_layers) - 1):
            weights.append([])
            for i in range(self.hidden_layers[k]):
                weights[k].append(self.components[
                                  last_component_index + i * self.hidden_layers[k + 1]:
                                  last_component_index + (i + 1) * self.hidden_layers[k + 1]])

            last_component_index = last_component_index + (i + 1) * self.hidden_layers[k + 1]
            if RECURENCE:
                for j in range(self.hidden_layers[k + 1]):
                    weights[k].append(self.components[
                        last_component_index + (self.hidden_layers[k + 1] * j):
                                      last_component_index + (self.hidden_layers[k + 1] * (j + 1))
                                      ])
                last_component_index = last_component_index + (self.hidden_layers[k + 1] * (j + 1))

            weights[k].append(self.components[last_bias_component_index:last_bias_component_index + self.hidden_layers[k + 1]])
            last_bias_component_index += self.hidden_layers[k + 1]
        return weights

    def map_to_range(self, value, old_range_min, old_range_max, new_range_min, new_range_max):
        old_span = old_range_max - old_range_min
        new_span = new_range_max - new_range_min
        value_scaled = float(value - old_range_min) / float(old_span)
        return new_range_min + (value_scaled * new_span)

    def get_gains(self):
        return self.components[len(self.components) - (2 * self.nr_of_non_input_neuron):
               len(self.components) - (1 * self.nr_of_non_input_neuron)]

    def get_time_constants(self):
        return self.components[len(self.components) - (1 * self.nr_of_non_input_neuron):]
