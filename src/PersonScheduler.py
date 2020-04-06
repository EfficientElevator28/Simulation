"""
Author: Austin Day
PersonScheduler.py
"""
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
import math

from src.Person import Person


class PersonScheduler:
    """
    PersonScheduler class
    Defines the scheduling for arrival and destinations of elevator passengers
    """

    def __init__(self, building, poisson_mean_density=.2, p_seed=1, seconds_to_schedule=100000):
        """
        Creates a PersonScheduler object.

        Arguments:
        building -- The building object for the simulation
        poisson_mean_density -- intensity (ie mean density) of the Poisson process; ==1 is mean 1 per second
        p_seed -- numpy RNG seed to give the same results with the same parameters
        """

        self.building = building
        self.poisson_mean_density = poisson_mean_density
        self.p_seed = p_seed
        self.seconds_to_schedule = seconds_to_schedule
        self.people_spawning = []
        self.people_spawning_min_index = 0

        self.setup_distribution()

    def setup_distribution(self):
        # Simulation window parameters
        x_min = 0
        x_max = self.seconds_to_schedule
        y_min = 0
        y_max = self.building.n_floors + 1  # num_floors + 1
        x_delta = x_max - x_min
        y_delta = y_max - y_min  # rectangle dimensions
        # area_total = x_delta * y_delta

        # Point process parameters
        # intensity (ie mean density) of the Poisson process; lambda=1 is mean 1 per second
        lambda0 = self.poisson_mean_density

        # Simulate Poisson point process
        np.random.seed(self.p_seed)
        num_points = scipy.stats.poisson(lambda0 * x_delta).rvs()  # Poisson number of points
        xx = x_delta * scipy.stats.uniform.rvs(0, 1, (num_points, 1)) + x_min  # x-coors of Poisson points
        xx_new = []
        for val in xx:
            xx_new.append(val[0])
        xx_new.sort()
        yy = y_delta * scipy.stats.uniform.rvs(0, 1, (num_points, 1)) + y_min  # y-coor: starting floor
        zz = y_delta * scipy.stats.uniform.rvs(0, 1, (num_points, 1)) + y_min  # z-coor: destination floor

        for val_arr in yy:
            val_arr[0] = int(math.floor(val_arr[0]))
        for val_arr in zz:
            val_arr[0] = int(math.floor(val_arr[0]))

        for i in range(0, len(xx)):
            self.people_spawning.append({
                "time": xx_new[i],
                "starting_floor": int(math.floor(yy[i][0])),
                "dest_floor": int(math.floor(zz[i][0])),
                "index": i
            })

    # Can be called after a simulator step to cut down on array search time (optional but much more efficient)
    # TODO
    def update_people_spawning_min_index(self, min_index):
        self.people_spawning_min_index = min_index

    # Returns the absolute time and list of people (or likely one person) that will need to be spawned next
    # relative to the current_timestamp
    def get_time_and_people_of_next_addition(self, current_timestamp):
        # This is what needs to be accessed by the RL step function to determine when to call the ML/when to add
        # people to the system

        if current_timestamp > self.seconds_to_schedule:
            return -1.0, []

        search_index = self.people_spawning_min_index
        max_index = len(self.people_spawning)
        while search_index < max_index and self.people_spawning[search_index]["time"] < current_timestamp:
            search_index = search_index + 1

        if search_index == max_index:
            if self.people_spawning[max_index]["time"] >= current_timestamp:
                return self.people_spawning[max_index]["time"], \
                       [Person(self.people_spawning[max_index]["starting_floor"],
                               self.people_spawning[max_index]["dest_floor"])]
            else:
                return -1.0, []
        else:
            # The end of the array of times/people hasn't been reached
            temp_people = []
            new_timestamp = self.people_spawning[search_index]["time"]
            while search_index <= max_index and abs(self.people_spawning[search_index]["time"] - new_timestamp) < .0001:
                temp_people.append(Person(self.people_spawning[search_index]["starting_floor"],
                                          self.people_spawning[search_index]["dest_floor"]))
                search_index = search_index + 1
            return new_timestamp, temp_people

    # Triggers button presses on floors by spawning people in
    def spawn_people(self, timestamp, people):
        self.building.last_floor_button_pressed = timestamp  # needed for rl step func v1
        for person in people:
            self.building.add_waiting_person(person)

