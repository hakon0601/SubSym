from direction import Direction
from cell_item import CellItem


class FlatlandAgent:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.food_eaten = 0
        self.poison_eaten = 0

    def sense_front_left_right(self, environment):
        north = environment.board[(self.y - 1) % environment.height][self.x]
        west = environment.board[self.y][(self.x - 1) % environment.width]
        east = environment.board[self.y][(self.x + 1) % environment.width]
        south = environment.board[(self.y + 1) % environment.height][self.x]
        if self.direction == Direction.north:
            return north, west, east
        elif self.direction == Direction.east:
            return east, north, south
        elif self.direction == Direction.south:
            return south, east, west
        elif self.direction == Direction.west:
            return west, south, north

    def move_forward(self, environment):
        if self.direction == Direction.north:
            self.y = (self.y - 1) % environment.height
        elif self.direction == Direction.east:
            self.x = (self.x + 1) % environment.width
        elif self.direction == Direction.south:
            self.y = (self.y + 1) % environment.height
        elif self.direction == Direction.west:
            self.x = (self.x - 1) % environment.width
        if environment.board[self.y][self.x] == CellItem.food:
            self.food_eaten += 1
        elif environment.board[self.y][self.x] == CellItem.poison:
            self.poison_eaten += 1
        environment.board[self.y][self.x] = CellItem.nothing

    def move_left(self):
        self.direction = Direction((self.direction.value - 1) % 4)

    def move_right(self):
        self.direction = Direction((self.direction.value + 1) % 4)
