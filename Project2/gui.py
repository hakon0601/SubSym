import Tkinter as tk

from population import Population

# Initial parameter values
GENOTYPE_POOL_SIZE = 10
ADULT_POOL_SIZE = 6
GENOTYPE_LENGTH = 20
PHENOTYPE_LENGTH = 20
DISCARD_OLD_ADULTS = False
GLOBAL_PARENT_COMPETITION = True


CROSSOVER_RATE = 0.5  # When two parents have a match, they have a X% chance of being recombined.
# When they are not combined they are simply copied (with mutations)
POINTS_OF_CROSSOVER = 5
MUTATION_RATE_INDIVIDUAL = 0.01  # X% av genomes are modified in ONE of their component
MUTATION_RATE_COMPONENT = 0.05  # Each component has a chance of mutating


class Gui(tk.Tk):
    def __init__(self, delay, generations, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.delay = delay
        self.generations = generations
        self.current_generation = 0

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

        self.radio_1_value = tk.BooleanVar()
        self.radio_1_value.set(DISCARD_OLD_ADULTS)
        tk.Label(self, text="Discard Old Adults").pack()
        tk.Radiobutton(self, text="Yes", variable=self.radio_1_value, value=True).pack()
        tk.Radiobutton(self, text="No", variable=self.radio_1_value, value=False).pack()
        self.radio_2_value = tk.BooleanVar()
        self.radio_2_value.set(GLOBAL_PARENT_COMPETITION)
        tk.Label(self, text="Global Parent Competition").pack()
        tk.Radiobutton(self, text="Yes", variable=self.radio_2_value, value=True).pack()
        tk.Radiobutton(self, text="No", variable=self.radio_2_value, value=False).pack()

        start_button = tk.Button(self, text="Start", width=20, command=self.start_EA)
        start_button.pack()

    def start_EA(self):
        self.population = Population()
        self.population.set_parameters(genotype_pool_size=self.horizontal_slider_1.get(),
                                       adult_pool_size=self.horizontal_slider_2.get(),
                                       genotype_length=self.horizontal_slider_3.get(),
                                       phenotype_length=self.horizontal_slider_3.get(), # Not a single slider
                                       discard_old_adults=self.radio_1_value.get(),
                                       global_parent_competition=self.radio_2_value.get(),
                                       crossover_rate=self.horizontal_slider_4.get(),
                                       mutation_rate_individual=self.horizontal_slider_5.get(),
                                       mutation_rate_component=self.horizontal_slider_6.get(),
                                       points_of_crossover=self.horizontal_slider_7.get()
                                       )
        self.population.initialize_genotypes()
        self.run_EA()

    def run_EA(self):
        # Evolve phenotypes from the pool of genotypes
        self.population.develop_all_genotypes_to_phenotypes()
        self.population.do_fitness_testing()
        self.population.refill_adult_pool()
        self.population.scale_fitness_of_adult_pool()
        self.population.select_parents_and_fill_genome_pool()
        #print "Best fitness value:", self.population.phenotype_adult_pool[0].fitness_value
        print "Average fitness in adult pool:", self.population.avg_fitness
        self.current_generation += 1
        if self.current_generation < self.horizontal_slider_8.get() and self.population.avg_fitness < 1.0:
            self.after(self.delay, lambda: self.run_EA())
        else:
            #TODO end rapport
            print "Best fitness value:", self.population.phenotype_adult_pool[0].fitness_value
            print "Average fitness in adult pool:", self.population.avg_fitness
            pass


if __name__ == "__main__":
    app = Gui(delay=1, generations=1000)
    app.mainloop()
