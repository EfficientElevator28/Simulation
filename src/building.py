"""
Author: Daniel Nichols
building.py
Defines a Building class, which contains elevators.
"""
from src.Person import Person
from src.floor import Floor
from math import floor as math_floor


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
        self.floors = [Floor(floor_num) for floor_num in range(0, n_floors)]  # floors is zero indexed
        self.last_floor_button_pressed = 0  # timestamp of when the last person pressed a floor button

    def get_floor_by_position(self, position):
        floor_idx = math_floor(position / self.floor_dist + .01)
        return self.floors[floor_idx]

    def get_position_of_floor(self, floor):
        return floor.floor_number * self.floor_dist

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

    # Adds people to people waiting on floor and presses the buttons
    def add_waiting_person(self, person):
        # (floors are zero indexed)
        self.floors[person.floor].people_waiting.append(person)
        if person.floor < person.destination:
            self.floors[person.floor].up_pressed = True
        else:
            self.floors[person.floor].up_pressed = False

    def get_total_people_in_system(self):
        total = 0
        for floor in self.floors:
            if floor.people_waiting is not None:
                total += len(floor.people_waiting)
        for elevator in self.elevators:
            if elevator.riders is not None:
                total += len(elevator.riders)
        return total
