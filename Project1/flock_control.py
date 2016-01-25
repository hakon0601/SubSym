from boid import Boid
from obstacle import Obstacle
from predator import Predator

from random import randrange
from math import sqrt, sin, cos, asin, pi, atan, atan2


class FlockControl:
    def __init__(self, screen_size, boid_radius=1, nr_of_boids=1, max_velocity=8, max_predator_velocity=10, separation_weight=0, alignment_weight=0, cohesion_weight=0, neighbour_distance=100, predator_radius=20, predator_neighbour_distance=150):
        self.screen_size = screen_size
        self.boid_radius = boid_radius
        self.neighbour_distance = neighbour_distance
        self.max_velocity = max_velocity
        self.max_predator_velocity = max_predator_velocity
        self.nr_of_boids = nr_of_boids
        self.predator_radius = predator_radius
        self.predator_neighbour_distance = predator_neighbour_distance

        self.boids = []
        self.obstacles = []
        self.predators = []

        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight
        self.cohesion_weight = cohesion_weight

        self.initialize_boids()

    def initialize_boids(self):
        for i in range(self.nr_of_boids):
            self.add_boid()

    def add_boid(self):
        boid = Boid(self.get_random_position(), self.boid_radius, self.get_random_velocity())
        self.boids.append(boid)
        return boid

    def get_random_position(self):
        return randrange(0, self.screen_size[0] - 1), randrange(0, self.screen_size[1] - 1)

    def get_random_velocity(self):
        return (randrange(-5, 5), randrange(-5, 5))

    def add_obastacle(self):
        # TODO place obstacle away from boids
        obs = Obstacle(screen_size=self.screen_size)
        self.obstacles.append(obs)
        return obs

    def add_predator(self):
        pred = Predator(self.get_random_position(), self.predator_radius, self.get_random_velocity())
        self.predators.append(pred)
        return pred

    def update_boids(self):
        for boid in self.boids:
            neighbours, avg_pos, avg_velocity = boid.get_neighbours(self.boids, self.neighbour_distance)
            if neighbours:
                sep = self.calculate_separation_force(boid, neighbours, avg_pos, self.separation_weight)
                align = self.calculate_alignment_force(boid, neighbours, avg_velocity)
                coh = self.calculate_cohersion_force(boid, neighbours, avg_pos)
                boid.velocity_x = int(round(max(self.max_velocity * -1, min(self.max_velocity, boid.velocity_x + sep[0] + align[0] + coh[0]))))
                boid.velocity_y = int(round(max(self.max_velocity * -1, min(self.max_velocity, boid.velocity_y + sep[1] + align[1] + coh[1]))))
                #print "sep: ", sep, "\t align: ", align, "\t coh: ", coh
            else:
                if boid.velocity_x > self.max_velocity/2:
                    boid.velocity_x -= 1
                if boid.velocity_y > self.max_velocity/2:
                    boid.velocity_y -= 1
            pred_neighbours, pred_avg_pos, pred_avg_velocity = boid.get_neighbours(self.predators, self.neighbour_distance)
            if pred_neighbours:
                pred_avoidance = self.calculate_separation_force(boid, pred_neighbours, pred_avg_pos, separation_weight=1)
                boid.velocity_x = int(round(max(self.max_velocity * -1, min(self.max_velocity, pred_avoidance[0]))))
                boid.velocity_y = int(round(max(self.max_velocity * -1, min(self.max_velocity, pred_avoidance[1]))))
                print "boid sees pred"
            obstacle_avoidance = self.calculate_obstacle_avoidance_force(boid)


        for moving_boid in self.boids:
            moving_boid.move_boid(self.screen_size)

    # Predators only use the cohesion force
    # TODO make predators follow boids and avoid obstacles
    def update_predators(self):
        for pred in self.predators:
            neighbours, avg_pos, avg_velocity = pred.get_neighbours(self.boids, self.predator_neighbour_distance)
            if neighbours:
                coh = self.calculate_cohersion_force(pred, neighbours, avg_pos)
                pred.velocity_x = int(max(self.max_predator_velocity * -1, min(self.max_velocity, coh[0])))
                pred.velocity_y = int(max(self.max_predator_velocity * -1, min(self.max_velocity, coh[1])))
            #obstacle_avoidance = self.calculate_obstacle_avoidance_force(pred)
            pred.move_boid(self.screen_size)

    def calculate_separation_force(self, boid, neighbours, avg_pos, separation_weight):
        x_diff_normalized = (boid.x - avg_pos[0])/float(self.neighbour_distance + neighbours[0].radius)
        y_diff_normalized = (boid.y - avg_pos[1])/float(self.neighbour_distance + neighbours[0].radius)
        # Will be large, when close, and small when far away
        new_velocity_x = self.max_velocity * (1 - (x_diff_normalized ** 3))
        new_velocity_y = self.max_velocity * (1 - (y_diff_normalized ** 3))
        if x_diff_normalized < 0:
            new_velocity_x *= -1
        if y_diff_normalized < 0:
            new_velocity_y *= -1

        return (new_velocity_x * separation_weight, new_velocity_y * separation_weight)

    def calculate_alignment_force(self, boid, neighbours, avg_velocity):
        x_diff_angle = (avg_velocity[0] - boid.velocity_x)
        y_diff_angle = (avg_velocity[1] - boid.velocity_y)
        return (x_diff_angle * self.alignment_weight, y_diff_angle * self.alignment_weight)

    def calculate_cohersion_force(self, boid, neighbours, avg_pos):
        x_diff_normalized = (avg_pos[0] - boid.x)/float(self.neighbour_distance)
        y_diff_normalized = (avg_pos[1] - boid.y)/float(self.neighbour_distance)
        new_velocity_x = self.max_velocity * x_diff_normalized
        new_velocity_y = self.max_velocity * y_diff_normalized

        return (new_velocity_x * self.cohesion_weight, new_velocity_y * self.cohesion_weight)

    def calculate_obstacle_avoidance_force(self, boid):
        if not self.obstacles:
            return False
        obs = self.obstacles[0]
        distance_to_closest_obstacle = boid.get_distance_to_other(obs) - obs.radius
        for i in range(1, len(self.obstacles)):
            dist_to_obs = boid.get_distance_to_other(self.obstacles[i]) - self.obstacles[i].radius
            if dist_to_obs < distance_to_closest_obstacle:
                obs = self.obstacles[i]
                distance_to_closest_obstacle = dist_to_obs

        center_to_center = max(boid.get_distance_to_other(obs), 1)
        if center_to_center < obs.radius + boid.radius:
            print "crisis, boid inside obstacle"
        if center_to_center < (obs.radius + self.neighbour_distance):
            boid_angle = self.rad_to_degrees(boid.get_angle())
            center_to_center_angle = self.rad_to_degrees(atan2(obs.y - boid.y, obs.x - boid.x))
            avoidance_angle = self.rad_to_degrees(asin(max(min((obs.radius + boid.radius)/center_to_center, 1), -1)))
            anglediff = (((boid_angle - center_to_center_angle) + 180) % 360) - 180
            if (anglediff <= avoidance_angle and anglediff >= -avoidance_angle):
                print "On collision_course"
                if anglediff < 0:
                    new_angle = (center_to_center_angle - avoidance_angle) % 360
                else:
                    new_angle = (center_to_center_angle + avoidance_angle) % 360
                boid_velocity = boid.get_velocity()
                boid.velocity_x = round(cos(new_angle*pi/float(180))*boid_velocity)
                boid.velocity_y = round(sin(new_angle*pi/float(180))*boid_velocity)
                return True
        return False

    def rad_to_degrees(self, rads):
        if rads < 0:
            rads = rads + (2*pi)
        return rads * 360 / (2*pi)

    def distance_between_points(self, x1, y1, x2, y2):
        return sqrt((x1 - x2)**2 + (y1 - y2)**2)





