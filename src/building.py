"""
Author: Daniel Nichols
building.py
Defines a Building class, which contains elevators.
"""


class Building:
    """
    Building class.
    """

    def __init__(self, name, elevators, n_floors):
        """
        Creates a building object.

        Arguments:
        name -- the name/id of this building.
        elevators -- a list of elevators in this building.
        """

        self.name = name
        self.elevators = elevators
        self.n_floors = n_floors

    def get_n_elevators(self):
        """
        Get the total number of elevators.
        """
        return len(self.elevators)

    def reset():
        """
        Resets every elevator in this building to its original position.
        """
        # TODO
        pass
