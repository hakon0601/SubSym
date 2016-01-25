from random import randrange

class Obstacle:
    def __init__(self, screen_size):
        self.radius = randrange(10, screen_size[1]/3)
        self.x = randrange(self.radius, screen_size[0] - self.radius)
        self.y = randrange(self.radius, screen_size[1] - self.radius)
