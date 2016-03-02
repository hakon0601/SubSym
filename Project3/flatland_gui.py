from __future__ import division
import Tkinter as tk
from direction import Direction
from cell_item import CellItem
from copy import deepcopy
import matplotlib.pyplot as plt
from constants import *


class FlatlandGui(tk.Tk):
    def __init__(self, delay, environments, agent, ann,
                 fitness_log_average, fitness_log_best, standard_deviation_log):
        tk.Tk.__init__(self)
        self.delay = delay
        self.flatlands = environments
        self.agents = [deepcopy(agent) for _ in range(len(environments))]
        self.ann = ann
        self.current_timestep = 0
        self.max_timestep = 60
        self.standard_deviation_log = standard_deviation_log
        self.fitness_log_best = fitness_log_best
        self.fitness_log_average = fitness_log_average
        self.title("Flatland")
        self.grid = {}
        self.food_texts = []
        self.poison_texts = []
        self.step_text = None
        self.cell_components = {}
        self.agent_component = [[] for _ in range(len(self.flatlands))]
        self.cell_size = (SCREEN_WIDTH - (max(2, len(environments) + 1)) * GRID_OFFSET) / \
                         (FLATLAND_WIDTH*max(2, len(environments)))
        self.canvas = tk.Canvas(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, background='white', borderwidth=0)
        self.canvas.pack(side="top", fill="both", expand="true")
        self.pause = True
        self.bind('<space>', self.toggle_pause)
        self.bind('<,>', self.decrease_simulation_speed)
        self.bind('<.>', self.increase_simulation_speed)
        self.draw_text()
        self.draw_board()
        self.update_text()
        self.draw_agents(self.agents)
        self.start_simulation()

    def toggle_pause(self, event=None):
        self.pause = not self.pause

    def increase_simulation_speed(self, event=None):
        self.delay = max(self.delay - 10, 1)

    def decrease_simulation_speed(self, event=None):
        self.delay += 10

    def draw_board(self):
        for i in range(len(self.flatlands)):
            offset = (i * (FLATLAND_WIDTH * self.cell_size + GRID_OFFSET))
            for y in range(FLATLAND_HEIGHT):
                for x in range(FLATLAND_WIDTH):
                    self.grid[i, x, y] = self.canvas.create_rectangle(
                            x * self.cell_size + GRID_OFFSET + offset,
                            y * self.cell_size + GRID_OFFSET,
                            (x + 1) * self.cell_size + GRID_OFFSET + offset,
                            (y + 1) * self.cell_size + GRID_OFFSET)
                    if self.flatlands[i].board[y][x] == CellItem.food:
                        self.cell_components[i, x, y] = self.canvas.create_oval(
                                x * self.cell_size + GRID_OFFSET + offset,
                                y * self.cell_size + GRID_OFFSET,
                                (x + 1) * self.cell_size + GRID_OFFSET + offset,
                                (y + 1) * self.cell_size + GRID_OFFSET,
                                fill="green")
                    elif self.flatlands[i].board[y][x] == CellItem.poison:
                        self.cell_components[i, x, y] = self.canvas.create_oval(
                                x * self.cell_size + GRID_OFFSET + offset,
                                y * self.cell_size + GRID_OFFSET,
                                (x + 1) * self.cell_size + GRID_OFFSET + offset,
                                (y + 1) * self.cell_size + GRID_OFFSET,
                                fill="red")

    def draw_text(self):
        for i in range(len(self.flatlands)):
            self.food_texts.append(self.canvas.create_text(
                    GRID_OFFSET + (i * (FLATLAND_WIDTH * self.cell_size + GRID_OFFSET)),
                    GRID_OFFSET + FLATLAND_HEIGHT * self.cell_size,
                    anchor=tk.NW))
            self.poison_texts.append(self.canvas.create_text(
                    GRID_OFFSET + (i * (FLATLAND_WIDTH * self.cell_size + GRID_OFFSET)),
                    GRID_OFFSET*1.5 + FLATLAND_HEIGHT * self.cell_size,
                    anchor=tk.NW))
        self.step_text = self.canvas.create_text(GRID_OFFSET, GRID_OFFSET/2)

    def update_text(self):
        for i in range(len(self.flatlands)):
            self.canvas.itemconfig(self.food_texts[i], text="Food eaten:" +
                                                            str(self.agents[i].food_eaten) + "/" +
                                                            str(self.flatlands[i].food_count))
            self.canvas.itemconfig(self.poison_texts[i], text="Poison eaten:" +
                                                              str(self.agents[i].poison_eaten) + "/" +
                                                              str(self.flatlands[i].poison_count))
        self.canvas.itemconfig(self.step_text, text="Step: " + str(self.current_timestep + 1))

    def draw_agents(self, agents):
        for i in range(len(self.flatlands)):
            agent = agents[i]
            for j in range(len(self.agent_component[i])):
                self.canvas.delete(self.agent_component[i][j])
            offset = (i * (FLATLAND_WIDTH * self.cell_size + GRID_OFFSET))
            self.agent_component[i] = []
            self.agent_component[i].append(self.canvas.create_polygon(
                agent.x * self.cell_size + (self.cell_size * 1/5) + GRID_OFFSET + offset,
                agent.y * self.cell_size + (self.cell_size * 2/5) + GRID_OFFSET,
                agent.x * self.cell_size + (self.cell_size * 2/5) + GRID_OFFSET + offset,
                agent.y * self.cell_size + (self.cell_size * 1/5) + GRID_OFFSET,
                agent.x * self.cell_size + (self.cell_size * 3/5) + GRID_OFFSET + offset,
                agent.y * self.cell_size + (self.cell_size * 1/5) + GRID_OFFSET,
                agent.x * self.cell_size + (self.cell_size * 4/5) + GRID_OFFSET + offset,
                agent.y * self.cell_size + (self.cell_size * 2/5) + GRID_OFFSET,
                agent.x * self.cell_size + (self.cell_size * 4/5) + GRID_OFFSET + offset,
                agent.y * self.cell_size + (self.cell_size * 3/5) + GRID_OFFSET,
                agent.x * self.cell_size + (self.cell_size * 3/5) + GRID_OFFSET + offset,
                agent.y * self.cell_size + (self.cell_size * 4/5) + GRID_OFFSET,
                agent.x * self.cell_size + (self.cell_size * 2/5) + GRID_OFFSET + offset,
                agent.y * self.cell_size + (self.cell_size * 4/5) + GRID_OFFSET,
                agent.x * self.cell_size + (self.cell_size * 1/5) + GRID_OFFSET + offset,
                agent.y * self.cell_size + (self.cell_size * 3/5) + GRID_OFFSET,
                outline='red', fill='blue', width=1))
            if agent.direction == Direction.north or agent.direction == Direction.east:
                self.agent_component[i].append(self.canvas.create_oval(
                    agent.x * self.cell_size + (self.cell_size * 12/20) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 6/20) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 14/20) - 1 + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 8/20) + GRID_OFFSET,
                    fill="yellow"
                ))
            if agent.direction == Direction.east or agent.direction == Direction.south:
                self.agent_component[i].append(self.canvas.create_oval(
                    agent.x * self.cell_size + (self.cell_size * 12/20) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 12/20) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 14/20) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 14/20) + GRID_OFFSET,
                    fill="yellow"
                ))
            if agent.direction == Direction.south or agent.direction == Direction.west:
                self.agent_component[i].append(self.canvas.create_oval(
                    agent.x * self.cell_size + (self.cell_size * 6/20) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 12/20) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 8/20) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 14/20) + GRID_OFFSET,
                    fill="yellow"
                ))
            if agent.direction == Direction.west or agent.direction == Direction.north:
                self.agent_component[i].append(self.canvas.create_oval(
                    agent.x * self.cell_size + (self.cell_size * 6/20) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 6/20) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 8/20) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 8/20) + GRID_OFFSET,
                    fill="yellow"
                ))
            if agent.direction == Direction.north or \
                    agent.direction == Direction.east or \
                    agent.direction == Direction.west:
                self.agent_component[i].append(self.canvas.create_line(
                    agent.x * self.cell_size + (self.cell_size * 2/5) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 1/5) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 1/2) + GRID_OFFSET + offset,
                    agent.y * self.cell_size - (self.cell_size * 1/5) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 3/5) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 1/5) + GRID_OFFSET
                ))
            if agent.direction == Direction.south or \
                    agent.direction == Direction.east or \
                    agent.direction == Direction.west:
                self.agent_component[i].append(self.canvas.create_line(
                    agent.x * self.cell_size + (self.cell_size * 2/5) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 4/5) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 1/2) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 6/5) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 3/5) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 4/5) + GRID_OFFSET
                ))
            if agent.direction == Direction.west or \
                    agent.direction == Direction.north or \
                    agent.direction == Direction.south:
                self.agent_component[i].append(self.canvas.create_line(
                    agent.x * self.cell_size + (self.cell_size * 1/5) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 2/5) + GRID_OFFSET,
                    agent.x * self.cell_size - (self.cell_size * 1/5) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 1/2) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 1/5) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 3/5) + GRID_OFFSET
                ))
            if agent.direction == Direction.east or \
                    agent.direction == Direction.north or \
                    agent.direction == Direction.south:
                self.agent_component[i].append(self.canvas.create_line(
                    agent.x * self.cell_size + (self.cell_size * 4/5) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 2/5) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 6/5) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 1/2) + GRID_OFFSET,
                    agent.x * self.cell_size + (self.cell_size * 4/5) + GRID_OFFSET + offset,
                    agent.y * self.cell_size + (self.cell_size * 3/5) + GRID_OFFSET
                ))

    def start_simulation(self):
        if not self.pause:
            if self.current_timestep < self.max_timestep:
                for i in range(len(self.flatlands)):
                    agent_sensor_output = self.agents[i].sense_front_left_right(self.flatlands[i])
                    ann_inputs = [1 if agent_sensor_output[0] == CellItem.food else 0,
                                  1 if agent_sensor_output[1] == CellItem.food else 0,
                                  1 if agent_sensor_output[2] == CellItem.food else 0,
                                  1 if agent_sensor_output[0] == CellItem.poison else 0,
                                  1 if agent_sensor_output[1] == CellItem.poison else 0,
                                  1 if agent_sensor_output[2] == CellItem.poison else 0]
                    prediction = self.ann.predict(inputs=ann_inputs)
                    best_index = prediction.argmax()
                    if best_index == 1:
                        self.agents[i].move_left()
                    elif best_index == 2:
                        self.agents[i].move_right()
                    self.agents[i].move_forward(self.flatlands[i])
                    # Remove cell component
                    if (i, self.agents[i].x, self.agents[i].y) in self.cell_components:
                        self.canvas.delete(self.cell_components[i, self.agents[i].x, self.agents[i].y])
                self.draw_agents(self.agents)
                self.update_text()
                self.current_timestep += 1
            else:
                print "Simulation over"
                self.plot_data(self.fitness_log_average, self.fitness_log_best, self.standard_deviation_log)
                return
        self.after(self.delay, lambda: self.start_simulation())

    @staticmethod
    def plot_data(fitness_log_average, fitness_log_best, standard_deviation_log):
        plt.figure(1)
        plt.subplot(211)
        plt.plot(fitness_log_average[-1], label="Average fitness")
        plt.plot(fitness_log_best[-1], label="Best fitness")
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

        plt.subplot(212)
        plt.plot(standard_deviation_log[-1], label="Standard deviation")
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
        plt.show()
