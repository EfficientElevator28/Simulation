"""
Author: Owen Barbour
"""


class Floor:
    """
    Floor class.
    """

    def __init__(self, floor_number, people_waiting=None, up_pressed=False, down_pressed=False):
        """
        inits the elevator.

        Parameters:
        floor_number -- floor of the building
        people_waiting -- array of initial people waiting for elevator
        up_pressed -- up button on floor is pressed
        down_pressed -- down button on floor is pressed
        """
        self.floor_number = floor_number
        self.up_pressed = up_pressed
        self.down_pressed = down_pressed

        if people_waiting is None:
            self.people_waiting = []
        else:
            self.people_waiting = people_waiting

    def pickup_going_up(self):
        self.down_pressed = False
        # TODO: remove each Person class from the people_waiting variable if their intention is to go down.
        #  Transfer these people to the elevator class
        pass

    def pickup_going_down(self):
        self.up_pressed = False
        # TODO: remove each Person class from the people_waiting variable if their intention is to go up.
        #  Transfer these people to the elevator class
        pass
