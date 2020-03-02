"""
Author: Austin Day
Person.py
Defines the Person class
"""


class Person:
    """
    Person Class
    Contains all the information and functionality needed for elevator passengers
    """

    def __init__(self, floor=-1, destination=-1):
        """
        Creates a person object.

        Arguments:
        floor -- the floor the individual is arriving on.
        destination -- the floor number the individual wants to go to
        """
        self.floor = floor
        self.destination = destination
        self.wait_time = 0  # includes time from first waiting for elevator to time getting off
        self.waiting_state = -2  # -2 = waiting for the elevator, -1 = waiting in the elevator, 0 = arrived

    def elevator_stop(self, elevator, floor, direction):
        """
        Signal to the person that the elevator has stopped. 
        Intended use: When the elevator stops on a floor, call this for all passengers waiting on the elevator so they can get off. Then call for all people waiting on that floor.

        Arguments:
        elevator -- the elevator object which has arrived
        floor -- the floor the elevator is on
        direction -- which way the elevator is travelling (1 = up, 0 = down)
        """

        # If the person is waiting for the elevator and it arrives on their floor,
        # board the elevator if it is going the right way
        if floor == self.floor and self.waiting_state == -2:
            if (direction == 1) == (self.floor < self.destination):
                elevator.add_rider(self)
                self.waiting_state = -1
                self.floor = -1

        # If the person is on the elevator, get off if it is on the right floor
        if self.waiting_state == -1 and floor == self.destination:
            elevator.remove_rider(self)
            self.waiting_state = 0

    def step(self):
        """
        Time step function, increments waiting time
        """
        if self.waiting_state != 0:
            self.wait_time += 1
