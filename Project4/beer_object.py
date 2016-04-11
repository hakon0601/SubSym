from constants import *
from random import randrange


class BeerObject():
    def __init__(self):
        self.size = randrange(1, BEER_MAX_SIZE + 1)
        self.x = randrange(0, WORLD_WIDTH - self.size - 1)
        self.y = 0
        self.range = []
        self.update_range()

    def update_range(self):
        self.range = range(self.x, self.x + self.size)

    # Moves the beer object one level down and returns True if it is moved below the board
    def drop_one_level(self):
        self.y += 1
        if self.y == WORLD_HEIGHT:
            return True
        return False

    def pull(self):
        self.y = WORLD_HEIGHT
