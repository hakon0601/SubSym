from constants import *


class BeerTrackerAgent:
    def __init__(self, x=0, size=5, agent_type=1):
        self.x = x
        self.size = size
        self.agent_type = agent_type
        self.range = []
        self.update_range()

    def update_range(self):
        self.range = []
        for i in range(self.x, self.x + self.size):
            self.range.append(i % WORLD_WIDTH)

    def get_sensor_array(self, environment):
        sensor_array = []
        for i in self.range:
            if i in environment.beer_object.range:
                sensor_array.append(1)
            else:
                sensor_array.append(0)
        # Wall detection sensors
        if self.agent_type == 2:
            sensor_array.append(1 if self.x == 0 else 0)
            sensor_array.append(1 if self.x == WORLD_WIDTH - 1 - self.size else 0)
        if CENTERED_NODE:
            if (sensor_array[0] == 0 and sensor_array[-1] == 0) and 1 in sensor_array[1:-1]:
                sensor_array.append(1)
            else:
                sensor_array.append(0)
        if FULL_NODE:
            if 0 in sensor_array[:INPUT_NODES]:
                sensor_array.append(0)
            else:
                sensor_array.append(1)
        return sensor_array

    def move_left(self, x_direction_size=1):
        if self.agent_type == 1:
            self.x = (self.x - x_direction_size) % WORLD_WIDTH
        elif self.agent_type == 2:
            self.x = max(0, self.x - x_direction_size)
        self.update_range()

    def move_right(self, x_direction_size=1):
        if self.agent_type == 1:
            self.x = (self.x + x_direction_size) % WORLD_WIDTH
        elif self.agent_type == 2:
            self.x = min(self.x + x_direction_size, WORLD_WIDTH - self.size)
        self.update_range()
