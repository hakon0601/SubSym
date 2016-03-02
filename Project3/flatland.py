from random import random
from cell_item import CellItem
from agent import FlatlandAgent


class Flatland:
    def __init__(self, width, height, food_probability, poison_probability):
        self.width = width
        self.height = height
        self.food_probability = food_probability
        self.poison_probability = poison_probability
        self.food_count = 0
        self.poison_count = 0
        self.board = self.construct_board()
        self.agent = FlatlandAgent()

    def construct_board(self):
        board = []
        for y in range(self.height):
            board.append([])
            for x in range(self.width):
                if random() <= self.food_probability:
                    board[y].append(CellItem.food)
                    self.food_count += 1
                elif random() <= self.poison_probability:
                    board[y].append(CellItem.poison)
                    self.poison_count += 1
                else:
                    board[y].append(CellItem.nothing)
        return board
