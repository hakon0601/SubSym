from __future__ import division
import Tkinter as tk
import matplotlib.pyplot as plt
from constants import *
from ctrann import Ann
from beertracker_world import BeerTrackerWorld
from math import floor
from phenotype import PhenotypeBeerTracker


class BeerTrackerGui(tk.Tk):
    def __init__(self, delay, environments, ann_weights, layers_list, activation_functions,
                 gains, time_constant,
                 fitness_log_average, fitness_log_best, standard_deviation_log):
        tk.Tk.__init__(self)
        self.delay = delay
        self.environments = environments
        self.ann = Ann(weights=ann_weights, hidden_layers=layers_list, activation_functions=activation_functions,
                       gains=gains, time_constants=time_constant)
        self.current_timestep = 0
        self.max_timestep = TIMESTEPS
        self.standard_deviation_log = standard_deviation_log
        self.fitness_log_best = fitness_log_best
        self.fitness_log_average = fitness_log_average
        self.title("Beer Tracker")
        self.grid = {}
        self.score_texts = []
        self.sensor_texts = []
        self.step_text = None
        self.beer_components = []
        self.agent_components = []
        self.pulling = [False for _ in range(len(environments))]
        self.cell_size = (SCREEN_WIDTH - (max(2, len(environments) + 1)) * GRID_OFFSET) / \
                         (WORLD_WIDTH * max(2, len(environments)))
        self.canvas = tk.Canvas(self, width=SCREEN_WIDTH, height=(self.cell_size + 4)*self.environments[0].height,
                                background='white', borderwidth=0)
        self.canvas.pack(side="top", fill="both", expand="true")
        self.pause = True
        self.bind('<space>', self.toggle_pause)
        self.bind('<n>', self.decrease_simulation_speed)
        self.bind('<m>', self.increase_simulation_speed)
        self.bind('<a>', self.move_agent_left)
        self.bind('<d>', self.move_agent_right)
        self.reset_button = tk.Button(self, text="Reset board", command=self.reset_gui_with_new_environment).pack()
        self.draw_text()
        self.draw_board()
        self.update_text()
        self.draw_agents()
        self.draw_beer_objects()
        self.run_simulation()

    def toggle_pause(self, event=None):
        self.pause = not self.pause

    def increase_simulation_speed(self, event=None):
        self.delay = max(self.delay - 10, 1)

    def decrease_simulation_speed(self, event=None):
        self.delay += 10

    def move_agent_left(self, event=None):
        self.environments[0].agent.move_left()

    def move_agent_right(self, event=None):
        self.environments[0].agent.move_right()

    def draw_board(self):
        for i in range(len(self.environments)):
            agent = self.environments[i].agent
            beer_object = self.environments[i].beer_object
            offset = (i * (WORLD_WIDTH * self.cell_size + GRID_OFFSET))
            for y in range(WORLD_HEIGHT):
                for x in range(WORLD_WIDTH):
                    self.grid[i, x, y] = self.canvas.create_rectangle(
                            x * self.cell_size + GRID_OFFSET + offset,
                            y * self.cell_size + GRID_OFFSET,
                            (x + 1) * self.cell_size + GRID_OFFSET + offset,
                            (y + 1) * self.cell_size + GRID_OFFSET)

    def draw_beer_objects(self):
        for k in range(len(self.beer_components)):
            for l in range(len(self.beer_components[k])):
                self.canvas.delete(self.beer_components[k][l])
        self.beer_components = []

        for i in range(len(self.environments)):
            beer_object = self.environments[i].beer_object
            offset = (i * (WORLD_WIDTH * self.cell_size + GRID_OFFSET))
            beer_components = []
            if beer_object.size > BEER_MAX_WANTED_SIZE:
                color = "red"
            else:
                color = "blue"
            for x in beer_object.range:
                beer_components.append(self.canvas.create_oval(
                        x * self.cell_size + GRID_OFFSET + offset,
                        beer_object.y * self.cell_size + GRID_OFFSET,
                        (x + 1) * self.cell_size + GRID_OFFSET + offset,
                        (beer_object.y + 1) * self.cell_size + GRID_OFFSET,
                        fill=color))
            self.beer_components.append(beer_components)

    def draw_text(self):
        for i in range(len(self.environments)):
            self.score_texts.append(self.canvas.create_text(
                    GRID_OFFSET + (i * (WORLD_WIDTH * self.cell_size + GRID_OFFSET)),
                    GRID_OFFSET + WORLD_HEIGHT * self.cell_size,
                    anchor=tk.NW))
            self.sensor_texts.append(self.canvas.create_text(
                    GRID_OFFSET + (i * (WORLD_WIDTH * self.cell_size + GRID_OFFSET)),
                    2 * GRID_OFFSET + WORLD_HEIGHT * self.cell_size,
                    anchor=tk.NW))
        self.step_text = self.canvas.create_text(GRID_OFFSET, GRID_OFFSET/2)

    def update_text(self):
        for i in range(len(self.environments)):
            self.canvas.itemconfig(self.score_texts[i], text="Score:" + str(self.environments[i].score))
            self.canvas.itemconfig(self.sensor_texts[i], text="Sensor:" + str(self.environments[i].agent.get_sensor_array(self.environments[i])))
        self.canvas.itemconfig(self.step_text, text="Step: " + str(self.current_timestep + 1))

    def draw_agents(self):
        for k in range(len(self.agent_components)):
            for l in range(len(self.agent_components[k])):
                self.canvas.delete(self.agent_components[k][l])
        self.agent_components = []

        for i in range(len(self.environments)):
            agent = self.environments[i].agent
            beer_object = self.environments[i].beer_object
            offset = (i * (WORLD_WIDTH * self.cell_size + GRID_OFFSET))
            agent_components = []
            color = "green"
            if self.pulling[i]:
                color = "yellow"
                self.pulling[i] = False
            for x in agent.range:
                agent_components.append(self.canvas.create_oval(
                        x * self.cell_size + GRID_OFFSET + offset,
                        (WORLD_HEIGHT - 1) * self.cell_size + GRID_OFFSET,
                        (x + 1) * self.cell_size + GRID_OFFSET + offset,
                        (WORLD_HEIGHT) * self.cell_size + GRID_OFFSET,
                        fill=color))
            self.agent_components.append(agent_components)

    #TODO fix better update
    '''
    def update_agents(self):
        for i in range(len(self.environments)):
            agent = self.environments[i].agent
            offset = (i * (WORLD_WIDTH * self.cell_size + GRID_OFFSET))
            for j in range(len(self.agent_components[i])):
                x = agent.range[j]
                self.canvas.itemconfig(self.agent_components[i][j],
                                       (x * self.cell_size + GRID_OFFSET + offset,
                        (WORLD_HEIGHT - 1) * self.cell_size + GRID_OFFSET,
                        (x + 1) * self.cell_size + GRID_OFFSET + offset,
                        (WORLD_HEIGHT) * self.cell_size + GRID_OFFSET))
    '''

    def start_simulation(self):
        self.current_timestep = 0
        self.run_simulation()

    def run_simulation(self):
        if not self.pause:
            if self.current_timestep < self.max_timestep:
                for i in range(len(self.environments)):
                    self.environments[i].drop_object_one_level()
                    agent_sensor_output = self.environments[i].agent.get_sensor_array(self.environments[i])
                    ann_inputs = agent_sensor_output
                    prediction = self.ann.predict(inputs=ann_inputs)
                    best_index = prediction.argmax()
                    # x_direction_size = int(floor(prediction[best_index] * (AGENT_MAX_NR_OF_STEPS + 1 - 0.0001)))
                    if ONE_HOT_OUTPUT:
                        if best_index == 0:
                            pass
                        elif best_index == 1:
                            self.environments[i].agent.move_right(x_direction_size=1)
                        elif best_index == 2:
                            self.environments[i].agent.move_right(x_direction_size=2)
                        elif best_index == 3:
                            self.environments[i].agent.move_right(x_direction_size=3)
                        elif best_index == 4:
                            self.environments[i].agent.move_right(x_direction_size=4)
                        elif best_index == 5:
                            self.environments[i].agent.move_left(x_direction_size=1)
                        elif best_index == 6:
                            self.environments[i].agent.move_left(x_direction_size=2)
                        elif best_index == 7:
                            self.environments[i].agent.move_left(x_direction_size=3)
                        elif best_index == 8:
                            self.environments[i].agent.move_left(x_direction_size=4)
                        elif self.environments[i].agent.agent_type == 3 and best_index == 9:
                            self.environments[i].pull_object()
                            self.pulling[i] = True
                    else:
                        if self.environments[i].agent.agent_type == 3 and prediction[2] > PULL_THRESHOLD:
                            self.environments[i].pull_object()
                            self.pulling[i] = True
                        elif prediction[0] > 0.5:
                            # Move right
                            if prediction[1] < 0.2:
                                pass
                            elif prediction[1] < 0.4:
                                self.environments[i].agent.move_right(x_direction_size=1)
                            elif prediction[1] < 0.6:
                                self.environments[i].agent.move_right(x_direction_size=2)
                            elif prediction[1] < 0.8:
                                self.environments[i].agent.move_right(x_direction_size=3)
                            else:
                                self.environments[i].agent.move_right(x_direction_size=4)
                        else:
                            # Move left
                            if prediction[1] < 0.2:
                                pass
                            elif prediction[1] < 0.4:
                                self.environments[i].agent.move_left(x_direction_size=1)
                            elif prediction[1] < 0.6:
                                self.environments[i].agent.move_left(x_direction_size=2)
                            elif prediction[1] < 0.8:
                                self.environments[i].agent.move_left(x_direction_size=3)
                            else:
                                self.environments[i].agent.move_left(x_direction_size=4)

                self.draw_agents()
                self.draw_beer_objects()
                self.update_text()
                self.current_timestep += 1
            else:
                print "Simulation over"
                #self.plot_data(self.fitness_log_average, self.fitness_log_best, self.standard_deviation_log)
                return
        self.after(self.delay, lambda: self.run_simulation())

    def reset_gui_with_new_environment(self, event=None):
        self.environments = [BeerTrackerWorld(width=self.environments[0].width,
                                              height=self.environments[0].height,
                                              agent_type=self.environments[0].agent.agent_type)
                             for _ in range(len(self.environments))]
        self.pause = True
        for key, val in self.grid.items():
            self.canvas.delete(val)
        self.draw_board()
        self.draw_agents()
        self.draw_beer_objects()
        self.update_text()
        self.start_simulation()

    @staticmethod
    def plot_data(fitness_log_average, fitness_log_best, standard_deviation_log):
        plt.figure(1)
        plt.subplot(211)
        plt.plot(fitness_log_average[-1], label="Average fitness")
        plt.plot(fitness_log_best[-1], label="Best fitness")
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

        plt.subplot(212)
        plt.plot(standard_deviation_log[-1], label="Standard deviation")
        #plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
        plt.show()
