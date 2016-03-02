import Tkinter as tk
import matplotlib.pyplot as plt
from math import ceil, log

from evolutionary_algorithm import EvolutionaryAlgorithm

# Initial parameter values
GENOTYPE_POOL_SIZE = 400
ADULT_POOL_SIZE = 300
GENOTYPE_LENGTH = 104
PHENOTYPE_LENGTH = 104
ADULT_SELECTION_PROTOCOL = 2
PARENT_SELECTION_PROTOCOL = 3
MUTATION_PROTOCOL = 1
PROBLEM = 1
CROSSOVER_RATE = 0.85  # When two parents have a match, they have a X% chance of being recombined.
# When they are not combined they are simply copied (with mutations)
POINTS_OF_CROSSOVER = 1
MUTATION_RATE = 0.55
SYMBOL_SET_SIZE = 10
TOURNAMENT_SLIP_THROUGH_PROBABILITY = 0.65
TARGET_SURPRISING_SEQUENCE_LENGTH = 5
TOURNAMENT_SIZE = 18
INITIAL_TEMPERATURE = 100
ZERO_THRESHOLD = 21
MAX_GENERATIONS = 1000


class Gui(tk.Tk):
    def __init__(self, delay, nr_of_runs=1, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.delay = delay
        self.nr_of_runs = nr_of_runs
        self.current_run = 0
        self.current_generation = 0
        self.fitness_log_average = []
        self.fitness_log_best = []
        self.standard_deviation_log = []
        self.ea = None
        self.build_parameter_menu()

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
        self.horizontal_slider_3 = tk.Scale(self, length=1000, from_=2, to=1000, orient=tk.HORIZONTAL,
                                            label="Genotype Length")
        self.horizontal_slider_3.set(GENOTYPE_LENGTH)
        self.horizontal_slider_3.pack()
        crossover_slider_group = tk.Frame(self)
        self.horizontal_slider_4 = tk.Scale(crossover_slider_group, length=500, from_=0.0, to=1.0, resolution=-1,
                                            orient=tk.HORIZONTAL, label="Crossover Rate")
        self.horizontal_slider_4.set(CROSSOVER_RATE)
        self.horizontal_slider_4.pack(side=tk.LEFT)
        self.horizontal_slider_5 = tk.Scale(self, length=1000, from_=0, to=1, resolution=-1, orient=tk.HORIZONTAL,
                                            label="Mutation Rate")
        self.horizontal_slider_5.set(MUTATION_RATE)
        self.horizontal_slider_5.pack()
        self.horizontal_slider_7 = tk.Scale(crossover_slider_group, length=500, from_=1, to=100, orient=tk.HORIZONTAL,
                                            label="Points of Crossover")
        self.horizontal_slider_7.set(POINTS_OF_CROSSOVER)
        self.horizontal_slider_7.pack(side=tk.LEFT)
        crossover_slider_group.pack(anchor=tk.W)
        self.horizontal_slider_8 = tk.Scale(self, length=1000, from_=0, to=300, orient=tk.HORIZONTAL,
                                            label="Zero-threshold")
        self.horizontal_slider_8.set(ZERO_THRESHOLD)
        self.horizontal_slider_8.pack()
        self.horizontal_slider_9 = tk.Scale(self, length=1000, from_=1, to=50, orient=tk.HORIZONTAL,
                                            label="Symbol Set Size")
        self.horizontal_slider_9.set(SYMBOL_SET_SIZE)
        self.horizontal_slider_9.pack(anchor=tk.W)
        tournament_slider_group = tk.Frame(self)
        self.horizontal_slider_11 = tk.Scale(tournament_slider_group, length=500, from_=3, to=500, orient=tk.HORIZONTAL,
                                            label="Tournament Size")
        self.horizontal_slider_11.set(TOURNAMENT_SIZE)
        self.horizontal_slider_11.pack(side=tk.LEFT)
        self.horizontal_slider_12 = tk.Scale(tournament_slider_group, length=500, from_=0, to=1, resolution=-1, orient=tk.HORIZONTAL,
                                             label="Tournament Slip-through Probability")
        self.horizontal_slider_12.set(TOURNAMENT_SLIP_THROUGH_PROBABILITY)
        self.horizontal_slider_12.pack(side=tk.LEFT)
        tournament_slider_group.pack(anchor=tk.W)
        self.horizontal_slider_13 = tk.Scale(self, length=1000, from_=1, to=1000, orient=tk.HORIZONTAL,
                                             label="Initial Temperature")
        self.horizontal_slider_13.set(INITIAL_TEMPERATURE)
        self.horizontal_slider_13.pack()
        self.horizontal_slider_14 = tk.Scale(self, length=1000, from_=1, to=10000, orient=tk.HORIZONTAL,
                                             label="Max Number of Generations")
        self.horizontal_slider_14.set(MAX_GENERATIONS)
        self.horizontal_slider_14.pack()

        self.mutation_protocol = tk.IntVar()
        self.mutation_protocol.set(MUTATION_PROTOCOL)
        radiogroup0 = tk.Frame(self)
        tk.Label(radiogroup0, text="Mutation Protocol").pack(anchor=tk.W)
        tk.Radiobutton(radiogroup0, text="Individual", variable=self.mutation_protocol, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(radiogroup0, text="Component", variable=self.mutation_protocol, value=2).pack(side=tk.LEFT)
        radiogroup0.pack(anchor=tk.W)

        self.adult_selection_protocol = tk.IntVar()
        self.adult_selection_protocol.set(ADULT_SELECTION_PROTOCOL)
        radiogroup1 = tk.Frame(self)
        tk.Label(radiogroup1, text="Adult Selection Protocol").pack(anchor=tk.W)
        tk.Radiobutton(radiogroup1, text="Full", variable=self.adult_selection_protocol,
                       command=self.control_pool_size_adult, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(radiogroup1, text="Over Production", variable=self.adult_selection_protocol,
                       command=self.control_pool_size_adult, value=2).pack(side=tk.LEFT)
        tk.Radiobutton(radiogroup1, text="Mixing", variable=self.adult_selection_protocol, value=3).pack(side=tk.LEFT)
        radiogroup1.pack(anchor=tk.W)

        self.parent_selection_protocol = tk.IntVar()
        self.parent_selection_protocol.set(PARENT_SELECTION_PROTOCOL)
        radiogroup2 = tk.Frame(self)
        tk.Label(radiogroup2, text="Parent Selection Protocol").pack(anchor=tk.W)
        tk.Radiobutton(radiogroup2, text="Fitness Proportionate", variable=self.parent_selection_protocol,
                       value=1).pack(side=tk.LEFT)
        tk.Radiobutton(radiogroup2, text="Sigma-scaling", variable=self.parent_selection_protocol,
                       value=2).pack(side=tk.LEFT)
        tk.Radiobutton(radiogroup2, text="Tournament selection", variable=self.parent_selection_protocol,
                       value=3).pack(side=tk.LEFT)
        tk.Radiobutton(radiogroup2, text="Boltzmann Selection", variable=self.parent_selection_protocol,
                       value=4).pack(side=tk.LEFT)
        radiogroup2.pack(anchor=tk.W)

        self.problem_type = tk.IntVar()
        self.problem_type.set(PROBLEM)
        radiogroup3 = tk.Frame(self)
        tk.Label(radiogroup3, text="Problem type").pack(anchor=tk.W)
        tk.Radiobutton(radiogroup3, text="One Max", variable=self.problem_type, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(radiogroup3, text="LOLZ Prefix", variable=self.problem_type, value=2).pack(side=tk.LEFT)
        tk.Radiobutton(radiogroup3, text="Surprising Sequence Local", variable=self.problem_type,
                       value=3).pack(side=tk.LEFT)
        tk.Radiobutton(radiogroup3, text="Surprising Sequence Global", variable=self.problem_type,
                       value=4).pack(side=tk.LEFT)
        radiogroup3.pack(anchor=tk.W)

        start_button = tk.Button(self, text="Start", width=20, command=self.start_simulation)
        start_button.pack()

    def control_pool_size_genotype(self, event):
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
            self.horizontal_slider_11.set(min(self.horizontal_slider_11.get(), self.horizontal_slider_2.get() // 2))

    def start_simulation(self):
        self.current_run = 0
        self.fitness_log_average = []
        self.fitness_log_best = []
        self.standard_deviation_log = []
        self.start_ea()

    def start_ea(self):
        self.ea = EvolutionaryAlgorithm(genotype_pool_size=self.horizontal_slider_1.get(),
                                        adult_pool_size=self.horizontal_slider_2.get(),
                                        genotype_length=self.horizontal_slider_3.get(),
                                        phenotype_length=self.horizontal_slider_3.get(),  # Not a single slider
                                        adult_selection_protocol=self.adult_selection_protocol.get(),
                                        parent_selection_protocol=self.parent_selection_protocol.get(),
                                        crossover_rate=self.horizontal_slider_4.get(),
                                        mutation_rate=self.horizontal_slider_5.get(),
                                        mutation_protocol=self.mutation_protocol.get(),
                                        points_of_crossover=self.horizontal_slider_7.get(),
                                        zero_threshold=self.horizontal_slider_8.get(),
                                        symbol_set_size=self.horizontal_slider_9.get(),
                                        tournament_size=self.horizontal_slider_11.get(),
                                        tournament_slip_through_probability=self.horizontal_slider_12.get(),
                                        initial_temperature=self.horizontal_slider_13.get(),
                                        problem=self.problem_type.get(),
                                        generations=self.horizontal_slider_14.get())
        self.current_generation = 0
        self.fitness_log_average.append([])
        self.fitness_log_best.append([])
        self.standard_deviation_log.append([])
        self.run_ea()

    def run_ea(self):
        self.ea.run_one_life_cycle()
        self.write_to_log()
        self.current_generation += 1
        if self.current_generation < self.horizontal_slider_14.get() and \
                self.ea.phenotype_adult_pool[0].fitness_value < 1.0:
            self.after(self.delay, lambda: self.run_ea())
        else:
            print "End"
            self.current_run += 1
            if self.current_run < self.nr_of_runs:
                self.start_ea()
            else:
                print "Average Generations:", sum([len(l) for l in self.fitness_log_average])/len(self.fitness_log_average)
                self.plot_data()

    def write_to_log(self):
        print "Gen:", "%.2d" % self.current_generation, "\tBest fitness:", \
            "%.3f" % round(self.ea.phenotype_adult_pool[0].fitness_value, 3), "\tAverage fitness:", \
            "%.3f" % round(self.ea.avg_fitness, 3), "\tStandard deviation: ", \
            "%.5f" % round(self.ea.standard_deviation, 3), "\tBest Phenotype:", \
            self.ea.phenotype_adult_pool[0].components
        if self.problem_type.get() > 2:
            print "Violations: ", self.ea.phenotype_adult_pool[0].violations
        self.fitness_log_average[self.current_run].append(self.ea.avg_fitness)
        self.fitness_log_best[self.current_run].append(self.ea.phenotype_adult_pool[0].fitness_value)
        self.standard_deviation_log[self.current_run].append(self.ea.standard_deviation)

    def plot_data(self):
        plt.figure(1)
        plt.subplot(311)
        plt.plot(self.fitness_log_average[-1], label="Average fitness")
        plt.plot(self.fitness_log_best[-1], label="Best fitness")
        #plt.legend(['y = Average fitness in adult pool', 'y = Best fitness in adult pool'], loc='lower right')
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)


        plt.subplot(312)
        plt.plot(self.fitness_log_best[-1])
        plt.legend(['y = Best fitness in adult pool'], loc='lower right')

        plt.subplot(313)
        plt.plot(self.standard_deviation_log[-1])
        plt.legend(['y = Standard deviation'], loc='upper right')
        plt.show()

if __name__ == "__main__":
    app = Gui(delay=1, nr_of_runs=1)
    app.mainloop()
