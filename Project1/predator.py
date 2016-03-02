from boid import Boid


class Predator(Boid):
    def __init__(self, (x, y), radius, (velocity_x, velocity_y)):
        Boid.__init__(self, (x, y), radius, (velocity_x, velocity_y))
