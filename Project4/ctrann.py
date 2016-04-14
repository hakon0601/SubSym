from activation_function import ActivationFunction
import numpy as np
from constants import *
from copy import copy
from math import exp


class CTRAnn:
    def __init__(self, weights, hidden_layers, activation_functions, gains, time_constants):
        self.weights = [np.array(weight) for weight in weights]
        self.hidden_layers = hidden_layers
        self.activation_functions = activation_functions
        self.gains = [[gains[sum(self.hidden_layers[1:(i - 1)]) + j]
                       for j in range(self.hidden_layers[i])]
                      for i in range(1, len(self.hidden_layers))]
        self.time_constants = [[time_constants[sum(self.hidden_layers[1:(i - 1)]) + j]
                                for j in range(self.hidden_layers[i])]
                               for i in range(1, len(self.hidden_layers))]

        self.neuron_internal_state = [np.zeros(self.hidden_layers[i]) for i in range(1, len(self.hidden_layers))]

    def activation_function(self, dot_product, activation_function):
        if activation_function == ActivationFunction.sigmoid:
            return self.sigmoid(dot_product)
        elif activation_function == ActivationFunction.hyperbolic_tangent:
            return self.tanh(dot_product)
        elif activation_function == ActivationFunction.rectify:
            return self.rectify(dot_product)
        elif activation_function == ActivationFunction.softmax:
            return self.softmax(dot_product)

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    @staticmethod
    def tanh(x):
        return np.tanh(x)

    @staticmethod
    def rectify(x):
        return np.maximum(0, x)

    @staticmethod
    def softmax(x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

    @staticmethod
    def calculate_state_output(internal_state, gains):
        return 1 / (1 + np.exp(-1 * np.array(internal_state) * gains))

    def predict(self, inputs):
        signal = np.array(inputs)
        for i in range(len(self.hidden_layers) - 1):
            if RECURENCE:
                signal = np.append(signal, self.calculate_state_output(self.neuron_internal_state[i], self.gains[i]))
            signal = np.append(signal, 1) # Bias node with a signal of 1
            dot_product = np.dot(signal, self.weights[i])
            signal = self.activation_function(dot_product, ActivationFunction(self.activation_functions[i]))
#            signal = self.calculate_state_output(dot_product, self.gains[i])
            self.leak_from_state(self.neuron_internal_state[i], signal, self.time_constants[i])
        return signal

    def leak_from_state(self, internal_state, signal, time_constants):
        # Recompute the derivative and update the internal state
        for i in range(len(signal)):
            internal_state[i] += (-internal_state[i] + signal[i]) / float(time_constants[i])
