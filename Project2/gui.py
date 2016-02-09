import Tkinter as tk

from population import Population

class Gui(tk.Tk):
    def __init__(self, delay, generations, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.delay = delay
        self.generations = generations
        self.current_generation = 0

        self.population = None
        self.start_EA()

    def start_EA(self):
        self.population = Population()
        self.run_EA()

    def run_EA(self):
        # Evolve phenotypes from the pool of genotypes
        self.population.develop_all_genotypes_to_phenotypes()
        self.population.do_fitness_testing()
        self.population.refill_adult_pool()
        self.population.scale_fitness_of_adult_pool()
        self.population.select_parents_and_fill_genome_pool()
        print "Best fitness value:", self.population.phenotype_adult_pool[0].fitness_value
        self.current_generation += 1
        if self.current_generation < self.generations:
            self.after(self.delay, lambda: self.run_EA())


if __name__ == "__main__":
    app = Gui(delay=1, generations=1000)
    app.mainloop()
