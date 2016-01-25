from flock_control import FlockControl
import Tkinter as tk

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 700
NR_OF_BOIDS = 1
BOID_RADIUS = 8
PREDATOR_RADIUS = 20
NEIGHBOUR_DISTANCE = BOID_RADIUS*10
PREDATOR_NEIGHBOUR_DISTANCE = PREDATOR_RADIUS*10
MAX_VELOCITY = 20
MAX_PREDATOR_VELOCITY = 10

class Gui(tk.Tk):
    def __init__(self, delay, draw_neighbourhood=True, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.delay = delay
        self.draw_neighbourhood = draw_neighbourhood
        self.title("Boids")

        self.canvas = tk.Canvas(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, background='white', borderwidth=0, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand="true")
        self.create_sliders()
        self.create_menu()

        self.boid_drawings = {}
        self.boid_neighbourhood_drawings = {}
        self.boid_direction_drawings = {}
        self.obstacle_drawings = []
        self.predator_drawings = []
        self.predator_direction_drawings = []
        self.predator_neighbourhood_drawings = []
        self.pause = False
        self.bind('<space>', self.toggle_pause)
        self.bind('<,>', self.decrease_simulation_speed)
        self.bind('<.>', self.increase_simulation_speed)
        self.flock_controller = FlockControl(screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT), boid_radius=BOID_RADIUS, nr_of_boids=NR_OF_BOIDS, max_velocity=MAX_VELOCITY, max_predator_velocity=MAX_PREDATOR_VELOCITY, neighbour_distance=NEIGHBOUR_DISTANCE, predator_radius=PREDATOR_RADIUS, predator_neighbour_distance=PREDATOR_NEIGHBOUR_DISTANCE)
        self.draw_board()
        self.run_simulation()

    def toggle_pause(self, event):
        self.pause = not self.pause

    def increase_simulation_speed(self, event):
        self.delay = max(self.delay - 10, 1)

    def decrease_simulation_speed(self, event):
        self.delay = self.delay + 10

    def create_menu(self):
        self.buttons = [
            tk.Button(self, text="Add Obstacle", width=20, command=self.add_obstacle),
            tk.Button(self, text="Remove Obstacles", width=20, command=self.remove_obstacles),
            tk.Button(self, text="Add Predator", width=20, command=self.add_predator),
            tk.Button(self, text="Remove Predators", width=20, command=self.remove_predators),
            tk.Button(self, text="Add Boid", width=20, command=self.add_boid)
        ]
        for btn in self.buttons:
            btn.pack(side=tk.LEFT)

    def create_sliders(self):
        self.horizontal_slider_1 = tk.Scale(self, length=200, from_=0, to=1000, orient=tk.HORIZONTAL,
                                            label="Separation", command=self.update_separation_weight)
        self.horizontal_slider_1.pack(side=tk.LEFT)
        self.horizontal_slider_2 = tk.Scale(self, length=200, from_=0, to=1000, orient=tk.HORIZONTAL,
                                            label="Alignment", command=self.update_alignment_weight)
        self.horizontal_slider_2.pack(side=tk.LEFT)
        self.horizontal_slider_3 = tk.Scale(self, length=200, from_=0, to=1000, orient=tk.HORIZONTAL,
                                            label="Cohesion", command=self.update_cohesion_weight)
        self.horizontal_slider_3.pack(side=tk.LEFT)

    def update_separation_weight(self, event):
        self.flock_controller.separation_weight = int(event)*0.001

    def update_alignment_weight(self, event):
        self.flock_controller.alignment_weight = int(event)*0.001

    def update_cohesion_weight(self, event):
        self.flock_controller.cohesion_weight = int(event)*0.001

    def add_boid(self):
        boid = self.flock_controller.add_boid()
        self.boid_drawings[len(self.flock_controller.boids) - 1] = self.canvas.create_oval(boid.x - BOID_RADIUS, boid.y - BOID_RADIUS, boid.x + BOID_RADIUS, boid.y + BOID_RADIUS, fill='blue', tags='rect')
        self.boid_direction_drawings[len(self.flock_controller.boids) - 1] = self.canvas.create_line(boid.x, boid.y, boid.x + boid.velocity_x*3, boid.y + boid.velocity_y*3, width=2)
        if self.draw_neighbourhood:
            self.boid_neighbourhood_drawings[len(self.flock_controller.boids) - 1] = self.canvas.create_oval(boid.x - NEIGHBOUR_DISTANCE, boid.y - NEIGHBOUR_DISTANCE, boid.x + NEIGHBOUR_DISTANCE, boid.y + NEIGHBOUR_DISTANCE, fill=None)

    def add_obstacle(self):
        obs = self.flock_controller.add_obastacle()
        obs_drawing = self.canvas.create_oval(obs.x - obs.radius, obs.y - obs.radius, obs.x + obs.radius, obs.y + obs.radius, fill='red')
        self.canvas.tag_lower(obs_drawing)
        self.obstacle_drawings.append(obs_drawing)

    def remove_obstacles(self):
        self.flock_controller.obstacles = []
        for i in range(len(self.obstacle_drawings)):
            self.canvas.delete(self.obstacle_drawings[i])
        self.obstacle_drawings = []

    def add_predator(self):
        pred = self.flock_controller.add_predator()
        self.predator_drawings.append(self.canvas.create_oval(pred.x - PREDATOR_RADIUS, pred.y - PREDATOR_RADIUS, pred.x + PREDATOR_RADIUS, pred.y + PREDATOR_RADIUS, fill='green', tags='rect'))
        self.predator_direction_drawings.append(self.canvas.create_line(pred.x, pred.y, pred.x + pred.velocity_x*3, pred.y + pred.velocity_y*3, width=2))
        self.predator_neighbourhood_drawings.append(self.canvas.create_oval(pred.x - PREDATOR_NEIGHBOUR_DISTANCE, pred.y - PREDATOR_NEIGHBOUR_DISTANCE, pred.x + PREDATOR_NEIGHBOUR_DISTANCE, pred.y + PREDATOR_NEIGHBOUR_DISTANCE, fill=None))

    def remove_predators(self):
        self.flock_controller.predators = []
        for i in range(len(self.predator_drawings)):
            self.canvas.delete(self.predator_drawings[i])
            self.canvas.delete(self.predator_direction_drawings[i])
            self.canvas.delete(self.predator_neighbourhood_drawings[i])
        self.predator_drawings = []
        self.predator_direction_drawings = []
        self.predator_neighbourhood_drawings = []

    def draw_board(self):
        for i in range(len(self.flock_controller.boids)):
            boid = self.flock_controller.boids[i]
            self.boid_drawings[i] = self.canvas.create_oval(boid.x - BOID_RADIUS, boid.y - BOID_RADIUS, boid.x + BOID_RADIUS, boid.y + BOID_RADIUS, fill='blue', tags='rect')
            self.boid_direction_drawings[i] = self.canvas.create_line(boid.x, boid.y, boid.x + boid.velocity_x*3, boid.y + boid.velocity_y*3, width=2)
            if self.draw_neighbourhood:
                self.boid_neighbourhood_drawings[i] = self.canvas.create_oval(boid.x - NEIGHBOUR_DISTANCE, boid.y - NEIGHBOUR_DISTANCE, boid.x + NEIGHBOUR_DISTANCE, boid.y + NEIGHBOUR_DISTANCE, fill=None)

    def update_board(self):
        for i in range(len(self.boid_drawings)):
            boid = self.flock_controller.boids[i]
            self.canvas.coords(self.boid_drawings[i], boid.x - BOID_RADIUS, boid.y - BOID_RADIUS, boid.x + BOID_RADIUS, boid.y + BOID_RADIUS)
            self.canvas.coords(self.boid_direction_drawings[i], boid.x, boid.y, boid.x + boid.velocity_x*300, boid.y + boid.velocity_y*300)
            if self.draw_neighbourhood:
                self.canvas.coords(self.boid_neighbourhood_drawings[i], boid.x - NEIGHBOUR_DISTANCE, boid.y - NEIGHBOUR_DISTANCE, boid.x + NEIGHBOUR_DISTANCE, boid.y + NEIGHBOUR_DISTANCE)
        for j in range(len(self.predator_drawings)):
            pred = self.flock_controller.predators[j]
            self.canvas.coords(self.predator_drawings[j], pred.x - PREDATOR_RADIUS, pred.y - PREDATOR_RADIUS, pred.x + PREDATOR_RADIUS, pred.y + PREDATOR_RADIUS)
            self.canvas.coords(self.predator_direction_drawings[j], pred.x, pred.y, pred.x + pred.velocity_x*300, pred.y + pred.velocity_y*300)
            self.canvas.coords(self.predator_neighbourhood_drawings[j], pred.x - PREDATOR_NEIGHBOUR_DISTANCE, pred.y - PREDATOR_NEIGHBOUR_DISTANCE, pred.x + PREDATOR_NEIGHBOUR_DISTANCE, pred.y + PREDATOR_NEIGHBOUR_DISTANCE)
        

    def run_simulation(self):
        if not self.pause:
            self.flock_controller.update_boids()
            self.flock_controller.update_predators()
            self.update_board()
        self.after(self.delay, lambda: self.run_simulation())

if __name__ == "__main__":
    app = Gui(delay=50, draw_neighbourhood=True)
    app.mainloop()


