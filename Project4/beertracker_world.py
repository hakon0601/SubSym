from random import random, randrange
from beertracker_agent import BeerTrackerAgent
from beer_object import BeerObject
from constants import *
from copy import deepcopy


class BeerTrackerWorld:
    def __init__(self, width, height, agent_type):
        self.width = width
        self.height = height
        self.agent = BeerTrackerAgent(x=randrange(WORLD_WIDTH - AGENT_SIZE), agent_type=agent_type)
        self.beer_object_index = 0
        self.nr_of_pulls = 0
        if agent_type == 3:
            self.beer_objects = [BeerObject() for _ in range(TIMESTEPS + 1)]
        else:
            self.beer_objects = [BeerObject() for _ in range((TIMESTEPS//WORLD_HEIGHT) + 1)]
        self.beer_object = self.beer_objects[0]
        # Two separate things should be measured, the ability to avoid big beers and the ability to catch the small ones
        # The first score list is [taken, avoided, partly avoided] for small, the second is the same for big beers.
        self.score = [[0, 0, 0], [0, 0, 0]]
        self.pull_score = [[0, 0, 0], [0, 0, 0]]
        # I need to keep the randomly spawned beer positions to be able to recreate a scenario.
        self.initial_beer_objects = deepcopy(self.beer_objects)
        self.initial_agent_x = self.agent.x

    def drop_object_one_level(self):
        if self.beer_object.drop_one_level():
            self.calculate_score_of_meal(self.score)
            self.beer_object_index += 1
            self.beer_object = self.beer_objects[self.beer_object_index]

    def pull_object(self):
        self.beer_object.pull()
        self.calculate_score_of_meal(self.pull_score)
        self.beer_object_index += 1
        self.nr_of_pulls += 1
        self.beer_object = self.beer_objects[self.beer_object_index]

    def calculate_score_of_meal(self, score):
        # Catch
        if self.agent.x <= self.beer_object.x and \
                                self.agent.x + self.agent.size >= self.beer_object.x + self.beer_object.size:
            if self.beer_object.size <= BEER_MAX_WANTED_SIZE:
                score[0][0] += 1
            else:
                score[1][0] += 1
        # Avoid
        elif self.agent.x > self.beer_object.x + self.beer_object.size or \
                                self.agent.x + self.agent.size < self.beer_object.x:
            if self.beer_object.size <= BEER_MAX_WANTED_SIZE:
                score[0][1] += 1
            else:
                score[1][1] += 1
        # Partly hit
        else:
            if self.beer_object.size <= BEER_MAX_WANTED_SIZE:
                score[0][2] += 1
            else:
                score[1][2] += 1
        self.beer_objects

    def reset(self):
        self.score = [[0, 0, 0], [0, 0, 0]]
        self.pull_score = [[0, 0, 0], [0, 0, 0]]
        self.beer_object_index = 0
        self.nr_of_pulls = 0
        self.beer_objects = deepcopy(self.initial_beer_objects)
        self.beer_object = self.beer_objects[self.beer_object_index]
        self.agent.x = self.initial_agent_x
        self.beer_object.update_range()
        self.agent.update_range()
