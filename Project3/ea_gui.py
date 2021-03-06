import Tkinter as tk
from direction import Direction
from flatland import Flatland
from evolutionary_algorithm import EvolutionaryAlgorithm
from flatland_gui import FlatlandGui
from constants import *


class EAGui(tk.Tk):
    def __init__(self, delay, nr_of_runs=1, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.delay = delay
        self.nr_of_runs = nr_of_runs
        self.current_run = 0
        self.current_generation = 0
        self.fitness_log_average = []
        self.fitness_log_best = []
        self.standard_deviation_log = []
        self.center_window()
        self.flatlands = None
        self.ea = None
        self.build_parameter_menu()

    def center_window(self):
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen
        w = 1000
        h = 900
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def build_parameter_menu(self):
        self.horizontal_slider_1 = tk.Scale(self, length=1000, from_=2, to=1000, orient=tk.HORIZONTAL,
                                            label="Genotype Pool Size", resolution=2,
                                            command=self.control_pool_size_genotype)
        self.horizontal_slider_1.set(GENOTYPE_POOL_SIZE)
        self.horizontal_slider_1.pack()
        self.horizontal_slider_2 = tk.Scale(self, length=1000, from_=2, to=1000, orient=tk.HORIZONTAL,
                                            label="Adult Pool Size", resolution=2, command=self.control_pool_size_adult)
        self.horizontal_slider_2.set(ADULT_POOL_SIZE)
        self.horizontal_slider_2.pack()
        self.horizontal_slider_3 = tk.Scale(self, length=1000, from_=0, to=1000, orient=tk.HORIZONTAL,
                                            label="Elitism", resolution=1, command=self.control_pool_size_adult)
        self.horizontal_slider_3.set(ELITISM)
        self.horizontal_slider_3.pack()

        ann_entry_group = tk.Frame(self)
        tk.Label(ann_entry_group, text="Hidden layers:").pack(side=tk.LEFT)
        self.hidden_layers = tk.StringVar()
        tk.Entry(ann_entry_group, textvariable=self.hidden_layers).pack(side=tk.LEFT)
        tk.Label(ann_entry_group, text="Activation functions (0:Sigmoid, 1:Hyperbolic tangent, 2:Rectify, 3:Softmax):",
                 padx=20).pack(side=tk.LEFT)
        self.activation_functions = tk.StringVar()
        self.activation_functions.set("3")
        tk.Entry(ann_entry_group, textvariable=self.activation_functions).pack(side=tk.LEFT)
        ann_entry_group.pack(anchor=tk.W)

        crossover_slider_group = tk.Frame(self)
        self.horizontal_slider_4 = tk.Scale(crossover_slider_group, length=500, from_=0.0, to=1.0, resolution=-1,
                                            orient=tk.HORIZONTAL, label="Crossover Rate")
        self.horizontal_slider_4.set(CROSSOVER_RATE)
        self.horizontal_slider_4.pack(side=tk.LEFT)
        self.horizontal_slider_5 = tk.Scale(self, length=1000, from_=0, to=1, resolution=-1, orient=tk.HORIZONTAL,
                                            label="Mutation Rate")
        self.horizontal_slider_5.set(MUTATION_RATE)
        self.horizontal_slider_5.pack()
        self.horizontal_slider_6 = tk.Scale(crossover_slider_group, length=500, from_=1, to=100, orient=tk.HORIZONTAL,
                                            label="Points of Crossover")
        self.horizontal_slider_6.set(POINTS_OF_CROSSOVER)
        self.horizontal_slider_6.pack(side=tk.LEFT)
        crossover_slider_group.pack(anchor=tk.W)

        self.horizontal_slider_7 = tk.Scale(self, length=1000, from_=1, to=50, orient=tk.HORIZONTAL,
                                            label="Symbol Set Size")
        self.horizontal_slider_7.set(SYMBOL_SET_SIZE)
        self.horizontal_slider_7.pack(anchor=tk.W)

        tournament_slider_group = tk.Frame(self)
        self.horizontal_slider_8 = tk.Scale(tournament_slider_group, length=500, from_=3, to=500, orient=tk.HORIZONTAL,
                                            label="Tournament Size")
        self.horizontal_slider_8.set(TOURNAMENT_SIZE)
        self.horizontal_slider_8.pack(side=tk.LEFT)
        self.horizontal_slider_9 = tk.Scale(tournament_slider_group, length=500, from_=0, to=1, resolution=-1,
                                            orient=tk.HORIZONTAL, label="Tournament Slip-through Probability")
        self.horizontal_slider_9.set(TOURNAMENT_SLIP_THROUGH_PROBABILITY)
        self.horizontal_slider_9.pack(side=tk.LEFT)
        tournament_slider_group.pack(anchor=tk.W)

        self.horizontal_slider_10 = tk.Scale(self, length=1000, from_=1, to=1000, orient=tk.HORIZONTAL,
                                             label="Initial Temperature")
        self.horizontal_slider_10.set(INITIAL_TEMPERATURE)
        self.horizontal_slider_10.pack()
        self.horizontal_slider_11 = tk.Scale(self, length=1000, from_=1, to=20, orient=tk.HORIZONTAL,
                                             label="Nr of Scenarios")
        self.horizontal_slider_11.set(NR_OF_SCENARIOS)
        self.horizontal_slider_11.pack(anchor=tk.W)
        self.horizontal_slider_12 = tk.Scale(self, length=1000, from_=1, to=500, orient=tk.HORIZONTAL,
                                             label="Max Number of Generations")
        self.horizontal_slider_12.set(MAX_GENERATIONS)
        self.horizontal_slider_12.pack()

        self.scenario_protocol = tk.IntVar()
        self.scenario_protocol.set(SCENARIO_PROTOCOL)
        scenario_protocol_group = tk.Frame(self)
        tk.Label(scenario_protocol_group, text="Scenario Protocol").pack(anchor=tk.W)
        tk.Radiobutton(scenario_protocol_group, text="Static", variable=self.scenario_protocol,
                       value=1).pack(side=tk.LEFT)
        tk.Radiobutton(scenario_protocol_group, text="Dynamic", variable=self.scenario_protocol,
                       value=2).pack(side=tk.LEFT)
        tk.Radiobutton(scenario_protocol_group, text="Static, test on random", variable=self.scenario_protocol,
                       value=3).pack(side=tk.LEFT)
        scenario_protocol_group.pack(anchor=tk.W)

        self.mutation_protocol = tk.IntVar()
        self.mutation_protocol.set(MUTATION_PROTOCOL)
        mutation_protocol_group = tk.Frame(self)
        tk.Label(mutation_protocol_group, text="Mutation Protocol").pack(anchor=tk.W)
        tk.Radiobutton(mutation_protocol_group, text="Individual", variable=self.mutation_protocol,
                       value=1).pack(side=tk.LEFT)
        tk.Radiobutton(mutation_protocol_group, text="Component", variable=self.mutation_protocol,
                       value=2).pack(side=tk.LEFT)
        mutation_protocol_group.pack(anchor=tk.W)

        self.adult_selection_protocol = tk.IntVar()
        self.adult_selection_protocol.set(ADULT_SELECTION_PROTOCOL)
        adult_selection_group = tk.Frame(self)
        tk.Label(adult_selection_group, text="Adult Selection Protocol").pack(anchor=tk.W)
        tk.Radiobutton(adult_selection_group, text="Full", variable=self.adult_selection_protocol,
                       command=self.control_pool_size_adult, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(adult_selection_group, text="Over Production", variable=self.adult_selection_protocol,
                       command=self.control_pool_size_adult, value=2).pack(side=tk.LEFT)
        tk.Radiobutton(adult_selection_group, text="Mixing", variable=self.adult_selection_protocol,
                       value=3).pack(side=tk.LEFT)
        adult_selection_group.pack(anchor=tk.W)

        self.parent_selection_protocol = tk.IntVar()
        self.parent_selection_protocol.set(PARENT_SELECTION_PROTOCOL)
        parent_selection_group = tk.Frame(self)
        tk.Label(parent_selection_group, text="Parent Selection Protocol").pack(anchor=tk.W)
        tk.Radiobutton(parent_selection_group, text="Fitness Proportionate", variable=self.parent_selection_protocol,
                       value=1).pack(side=tk.LEFT)
        tk.Radiobutton(parent_selection_group, text="Sigma-scaling", variable=self.parent_selection_protocol,
                       value=2).pack(side=tk.LEFT)
        tk.Radiobutton(parent_selection_group, text="Tournament selection", variable=self.parent_selection_protocol,
                       value=3).pack(side=tk.LEFT)
        tk.Radiobutton(parent_selection_group, text="Boltzmann Selection", variable=self.parent_selection_protocol,
                       value=4).pack(side=tk.LEFT)
        parent_selection_group.pack(anchor=tk.W)

        start_button = tk.Button(self, text="Start", width=20, command=self.start_simulation)
        start_button.pack()

    def control_pool_size_genotype(self, event=None):
        if self.adult_selection_protocol.get() == 1:
            self.horizontal_slider_2.set(self.horizontal_slider_1.get())
        elif self.adult_selection_protocol.get() == 2:
            self.horizontal_slider_2.set(min(self.horizontal_slider_2.get(), self.horizontal_slider_1.get() - 2))

    def control_pool_size_adult(self, event=None):
        if self.adult_selection_protocol.get() == 1:
            self.horizontal_slider_1.set(self.horizontal_slider_2.get())
        elif self.adult_selection_protocol.get() == 2:
            self.horizontal_slider_1.set(max(self.horizontal_slider_1.get(), self.horizontal_slider_2.get() - 6))
        if self.parent_selection_protocol.get() == 3:
            self.horizontal_slider_8.set(min(self.horizontal_slider_8.get(), self.horizontal_slider_2.get() // 2))
        self.horizontal_slider_3.set(min(self.horizontal_slider_3.get(), self.horizontal_slider_2.get()))

    def start_simulation(self):
        self.current_run = 0
        self.fitness_log_average = []
        self.fitness_log_best = []
        self.standard_deviation_log = []
        self.start_ea()

    def start_ea(self):
        self.parse_ann_input()
        self.ea = EvolutionaryAlgorithm(genotype_pool_size=self.horizontal_slider_1.get(),
                                        adult_pool_size=self.horizontal_slider_2.get(),
                                        elitism=self.horizontal_slider_3.get(),
                                        genotype_length=self.genotype_size,
                                        phenotype_length=self.genotype_size,
                                        adult_selection_protocol=self.adult_selection_protocol.get(),
                                        parent_selection_protocol=self.parent_selection_protocol.get(),
                                        crossover_rate=self.horizontal_slider_4.get(),
                                        mutation_rate=self.horizontal_slider_5.get(),
                                        mutation_protocol=self.mutation_protocol.get(),
                                        points_of_crossover=self.horizontal_slider_6.get(),
                                        symbol_set_size=self.horizontal_slider_7.get(),
                                        tournament_size=self.horizontal_slider_8.get(),
                                        tournament_slip_through_probability=self.horizontal_slider_9.get(),
                                        initial_temperature=self.horizontal_slider_10.get(),
                                        hidden_layers=self.layers_list,
                                        activation_functions=self.activations_list,
                                        generations=self.horizontal_slider_12.get())

        self.flatlands = [self.initialize_board() for _ in range(self.horizontal_slider_11.get())]
        self.current_generation = 0
        self.fitness_log_average.append([])
        self.fitness_log_best.append([])
        self.standard_deviation_log.append([])
        self.run_ea()

    def run_ea(self):
        self.ea.run_one_life_cycle(self.flatlands)
        if self.scenario_protocol.get() != 1:
            self.flatlands = [self.initialize_board() for _ in range(len(self.flatlands))]
        self.write_to_log()
        self.current_generation += 1
        if self.current_generation < self.horizontal_slider_12.get() and \
                self.ea.phenotype_adult_pool[0].fitness_value < 1.0:
            self.after(self.delay, lambda: self.run_ea())
        elif self.current_run < self.nr_of_runs - 1:
            self.current_run += 1
            print "Current run", self.current_run
            self.start_ea()
        else:
            self.end_ea_run_visualisation()

    def end_ea_run_visualisation(self):
        print "Avg best fitness:", sum([self.fitness_log_best[i][-1] for i in range(len(self.fitness_log_best))]) / \
                                   len(self.fitness_log_best)
        print "Best fitness:", max([self.fitness_log_best[i][-1] for i in range(len(self.fitness_log_best))])
        weights = self.ea.phenotype_adult_pool[0].prepare_weights_for_ann()
        FlatlandGui(delay=300,
                    environments=self.flatlands,
                    ann_weights=weights,
                    layers_list=self.layers_list,
                    activation_functions=self.activations_list,
                    fitness_log_average=self.fitness_log_average,
                    fitness_log_best=self.fitness_log_best,
                    standard_deviation_log=self.standard_deviation_log)
        print "Average Generations:", \
            sum([len(l) for l in self.fitness_log_average]) / len(self.fitness_log_average)

    @staticmethod
    def initialize_board():
        flatland = Flatland(width=FLATLAND_WIDTH, height=FLATLAND_HEIGHT,
                            food_probability=FOOD_PROBABILITY,
                            poison_probability=POISON_PROBABILITY)
        return flatland

    def parse_ann_input(self):
        if self.hidden_layers.get() != '':
            self.layers_list = [INPUT_NODES] + \
                               map(int, self.hidden_layers.get().replace(" ", "").split(",")) + \
                               [OUTPUT_NODES]
        else:
            self.layers_list = [INPUT_NODES, OUTPUT_NODES]
        self.activations_list = map(int, str(self.activation_functions.get()).replace(" ", "").split(","))
        self.genotype_size = sum([self.layers_list[i] * self.layers_list[i + 1]
                                  for i in range(len(self.layers_list) - 1)])

    def write_to_log(self):
        print "Gen:", "%.2d" % self.current_generation, "\tBest fitness:", \
            "%.3f" % round(self.ea.phenotype_adult_pool[0].fitness_value, 3), "\tAverage fitness:", \
            "%.3f" % round(self.ea.avg_fitness, 3), "\tStandard deviation: ", \
            "%.5f" % round(self.ea.standard_deviation, 3), "\tBest Phenotype:", \
            self.ea.phenotype_adult_pool[0].components
        self.fitness_log_average[self.current_run].append(self.ea.avg_fitness)
        self.fitness_log_best[self.current_run].append(self.ea.phenotype_adult_pool[0].fitness_value)
        self.standard_deviation_log[self.current_run].append(self.ea.standard_deviation)

if __name__ == "__main__":
    app = EAGui(delay=1, nr_of_runs=1)
    app.mainloop()
