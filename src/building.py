"""
Author: Daniel Nichols
building.py
Defines a Building class, which contains elevators.
"""


class Building:
    """
    Building class.
    """

    def __init__(self, name, elevators, n_floors, floor_dist):
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
