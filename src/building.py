"""
Author: Daniel Nichols
building.py
Defines a Building class, which contains elevators.
"""
from src.floor import Floor


class Building:
    """
    Building class.
    """

    def __init__(self, name, elevators, n_floors, floor_dist=4.5, elev_height=2.5):
        """
        Creates a building object.

        Arguments:
        name -- the name/id of this building.
        elevators -- a list of elevators in this building.
        n_floors -- number fo floors in building
        floor_dist -- distance between floors (meters)
        """

        self.name = name
        self.elevators = elevators
        self.n_floors = n_floors
        self.floor_dist = floor_dist
        self.elev_height = elev_height
        # TODO: create a list of floors to add people to when they first arrive and are waiting for an elevator.
        #  In progress.
        self.floors = [Floor(floor_num) for floor_num in range(0, n_floors)]

    def get_n_elevators(self):
        """
        Get the total number of elevators.
        """
        return len(self.elevators)

    def reset(self):
        """
        Resets every elevator in this building to its original position.
        """
        # TODO
        pass

    # TODO: Create a function that adds a person to a floor where they wait
    # def add_waiting_person(self, person):
