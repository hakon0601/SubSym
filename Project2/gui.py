import Tkinter as tk
import matplotlib.pyplot as plt

from population import Population

# Initial parameter values
GENOTYPE_POOL_SIZE = 10
ADULT_POOL_SIZE = 6
GENOTYPE_LENGTH = 20
PHENOTYPE_LENGTH = 20
ADULT_SELECTION_PROTOCOL = 1
PARENT_SELECTION_PROTOCOL = 1


CROSSOVER_RATE = 0.5  # When two parents have a match, they have a X% chance of being recombined.
# When they are not combined they are simply copied (with mutations)
POINTS_OF_CROSSOVER = 5
MUTATION_RATE_INDIVIDUAL = 0.01  # X% av genomes are modified in ONE of their component
MUTATION_RATE_COMPONENT = 0.05  # Each component has a chance of mutating

ZERO_THRESHOLD = 4


class Gui(tk.Tk):
    def __init__(self, delay, generations, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.delay = delay
        self.generations = generations
        self.current_generation = 0

        self.fitness_log_average = []
        self.fitness_log_best = []
        self.population = None
        self.build_parameter_menu()

    def build_parameter_menu(self):
        self.horizontal_slider_1 = tk.Scale(self, length=200, from_=0, to=1000, orient=tk.HORIZONTAL,
                                            label="Genotype Pool Size", resolution=2)
        self.horizontal_slider_1.set(GENOTYPE_POOL_SIZE)
        self.horizontal_slider_1.pack()
        self.horizontal_slider_2 = tk.Scale(self, length=200, from_=0, to=1000, orient=tk.HORIZONTAL,
                                            label="Adult Pool Size")
        self.horizontal_slider_2.set(ADULT_POOL_SIZE)
        self.horizontal_slider_2.pack()
        self.horizontal_slider_3 = tk.Scale(self, length=200, from_=0, to=300, orient=tk.HORIZONTAL,
                                            label="Genotype Length")
        self.horizontal_slider_3.set(GENOTYPE_LENGTH)
        self.horizontal_slider_3.pack()
        self.horizontal_slider_4 = tk.Scale(self, length=200, from_=0.0, to=1.0, resolution=-1, orient=tk.HORIZONTAL,
                                            label="Crossover Rate")
        self.horizontal_slider_4.set(CROSSOVER_RATE)
        self.horizontal_slider_4.pack()
        self.horizontal_slider_5 = tk.Scale(self, length=200, from_=0, to=1, resolution=-1, orient=tk.HORIZONTAL,
                                            label="Individual Mutation Rate")
        self.horizontal_slider_5.set(MUTATION_RATE_INDIVIDUAL)
        self.horizontal_slider_5.pack()
        self.horizontal_slider_6 = tk.Scale(self, length=200, from_=0, to=1, resolution=-1, orient=tk.HORIZONTAL,
                                            label="Component Mutation Rate")
        self.horizontal_slider_6.set(MUTATION_RATE_COMPONENT)
        self.horizontal_slider_6.pack()
        self.horizontal_slider_7 = tk.Scale(self, length=200, from_=0, to=100, orient=tk.HORIZONTAL,
                                            label="Points of Crossover")
        self.horizontal_slider_7.set(POINTS_OF_CROSSOVER)
        self.horizontal_slider_7.pack()
        self.horizontal_slider_8 = tk.Scale(self, length=200, from_=0, to=10000, orient=tk.HORIZONTAL,
                                            label="Max Number of Generations")
        self.horizontal_slider_8.set(self.generations)
        self.horizontal_slider_8.pack()

        self.adult_selection_protocol = tk.IntVar()
        self.adult_selection_protocol.set(ADULT_SELECTION_PROTOCOL)
        tk.Label(self, text="Adult Selection Protocol").pack(anchor=tk.W)
        tk.Radiobutton(self, text="Full", variable=self.adult_selection_protocol, value=1).pack(anchor=tk.W)
        tk.Radiobutton(self, text="Over Production", variable=self.adult_selection_protocol, value=2).pack(anchor=tk.W)
        tk.Radiobutton(self, text="Mixing", variable=self.adult_selection_protocol, value=3).pack(anchor=tk.W)
        self.radio_2_value = tk.IntVar()
        self.radio_2_value.set(PARENT_SELECTION_PROTOCOL)
        tk.Label(self, text="Parent Selection Protocol").pack(anchor=tk.W)
        tk.Radiobutton(self, text="Fitness Proportionate", variable=self.radio_2_value, value=1).pack(anchor=tk.W)
        tk.Radiobutton(self, text="Sigma-scaling", variable=self.radio_2_value, value=2).pack(anchor=tk.W)
        tk.Radiobutton(self, text="Tournament selection", variable=self.radio_2_value, value=3).pack(anchor=tk.W)
        tk.Radiobutton(self, text="4th Selection Protocol", variable=self.radio_2_value, value=4).pack(anchor=tk.W)

        start_button = tk.Button(self, text="Start", width=20, command=self.start_EA)
        start_button.pack()

    def start_EA(self):
        self.population = Population()
        self.population.set_parameters(genotype_pool_size=self.horizontal_slider_1.get(),
                                       adult_pool_size=self.horizontal_slider_2.get(),
                                       genotype_length=self.horizontal_slider_3.get(),
                                       phenotype_length=self.horizontal_slider_3.get(),  # Not a single slider
                                       adult_selection_protocol=self.adult_selection_protocol.get(),
                                       parent_selection_protocol=self.radio_2_value.get(),
                                       crossover_rate=self.horizontal_slider_4.get(),
                                       mutation_rate_individual=self.horizontal_slider_5.get(),
                                       mutation_rate_component=self.horizontal_slider_6.get(),
                                       points_of_crossover=self.horizontal_slider_7.get()
                                       )
        self.population.initialize_genotypes()
        self.generations = self.horizontal_slider_8.get()
        self.current_generation = 0
        self.fitness_log_average = []
        self.fitness_log_best = []



        self.run_EA()

    def run_EA(self):
        # Evolve phenotypes from the pool of genotypes
        self.population.develop_all_genotypes_to_phenotypes()
        self.population.do_fitness_testing()
        self.population.refill_adult_pool()
        self.population.scale_fitness_of_adult_pool()
        self.population.select_parents_and_fill_genome_pool()
        #print "Best fitness value:", self.population.phenotype_adult_pool[0].fitness_value
        #print "Average fitness in adult pool:", self.population.avg_fitness
        print "Current Generation:", self.current_generation
        self.fitness_log_average.append(self.population.avg_fitness)
        self.fitness_log_best.append(self.population.phenotype_adult_pool[0].fitness_value)
        self.current_generation += 1
        if self.current_generation < self.horizontal_slider_8.get() and \
                        self.population.phenotype_adult_pool[0].fitness_value < 1.0:
            self.after(self.delay, lambda: self.run_EA())
        else:
            #TODO end rapport
            print "Best fitness value:", self.population.phenotype_adult_pool[0].fitness_value
            print "Average fitness in adult pool:", self.population.avg_fitness
            print "Generation", self.current_generation
            self.plot_data()

    def plot_data(self):
        plt.figure(1)
        plt.subplot(211)
        plt.plot(self.fitness_log_average)
        plt.legend(['x = Generations\ny = Average fitness in adult pool'], loc='lower right')

        plt.subplot(212)
        plt.plot(self.fitness_log_best)
        plt.legend(['x = Generations\ny = Best fitness in adult pool'], loc='lower right')
        plt.show()

if __name__ == "__main__":
    app = Gui(delay=1, generations=1000)
    app.mainloop()
