from random import randrange

class Obstacle:
    def __init__(self, (x, y), radius):
        self.radius = radius
        self.x = x
        self.y = y
