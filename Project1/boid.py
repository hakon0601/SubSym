from math import sqrt, pi, sin, cos, atan2


class Boid:
    def __init__(self, (x, y), radius, (velocity_x, velocity_y)):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def move_boid(self, screen_size):
        self.x = (self.x + self.velocity_x) % screen_size[0]
        self.y = (self.y + self.velocity_y) % screen_size[1]

    def get_distance_to_other(self, other):
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def get_angle(self):
        return atan2(self.velocity_y, self.velocity_x)

    def get_velocity(self):
        return sqrt(self.velocity_x**2 + self.velocity_y**2)

    # Retrieve all neighbours and their average position and velocity. Also returns the position of the closest neighbour
    def get_neighbours(self, boids, neighbour_distance):
        neighbours = []
        sum_pos_x = 0
        sum_pos_y = 0
        sum_velocity_x = 0
        sum_velocity_y = 0
        closest_pos = (0, 0)
        shortest_distance = float('inf')
        for potential_neighbour in boids:
            if potential_neighbour != self:
                distance_to_neighbour = self.get_distance_to_other(potential_neighbour)
                if distance_to_neighbour <= neighbour_distance + potential_neighbour.radius:
                    neighbours.append(potential_neighbour)
                    sum_pos_x += potential_neighbour.x
                    sum_pos_y += potential_neighbour.y
                    sum_velocity_x += potential_neighbour.velocity_x
                    sum_velocity_y += potential_neighbour.velocity_y
                    if distance_to_neighbour < shortest_distance:
                        shortest_distance = distance_to_neighbour
                        closest_pos = (potential_neighbour.x, potential_neighbour.y)
        if not neighbours:
            return [], (0, 0), (0, 0), (0, 0)
        avg_pos = (int(sum_pos_x/len(neighbours)), int(sum_pos_y/len(neighbours)))
        avg_velocity = (int(sum_velocity_x/len(neighbours)), int(sum_velocity_y/(len(neighbours))))
        return neighbours, avg_pos, avg_velocity, closest_pos