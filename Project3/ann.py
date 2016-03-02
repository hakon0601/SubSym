from activation_function import ActivationFunction
import numpy as np


class Ann:
    def __init__(self, weights, hidden_layers, activation_functions):
        self.weights = [np.array(weight) for weight in weights]
        self.hidden_layers = hidden_layers
        self.activation_functions = activation_functions

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

    def predict(self, inputs):
        prev_val = inputs
        for i in range(len(self.hidden_layers) - 1):
            dot_product = np.dot(prev_val, self.weights[i])
            prev_val = self.activation_function(dot_product, ActivationFunction(self.activation_functions[i]))
        return prev_val
