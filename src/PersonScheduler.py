"""
Author: Austin Day
PersonScheduler.py
"""
import numpy as np


class PersonScheduler:
    """
    PersonScheduler class
    Defines the scheduling for arrival and destinations of elevator passengers
    """

    def __init__(self, building, step_time_scale, expected_destinations=None):
        """
        Creates a PersonScheduler object.

        Arguments:
        building -- The building object for the simulation
        step_time_scale -- The amount of time elapsed between each simulation step (in ms)
        expected_destinations --    A dictionary keyed on ints representing days of the week (-1 = default, 0-6 = monday-sunday) 
                                    each key storing a dict keyed on timestamps representing the time of day this 'schedule' starts (military time)
                                    each timestamp key holding a list representing hourly rates of button presses on each floor. It's complicated.
        """

        self.building = building
        self.step_time_scale = step_time_scale
        self.expected_destinations = expected_destinations  # Expect 1 button press per floor every hour
        if expected_destinations is None:
            self.expected_destinations = {-1: {"0000": [1 for i in range(building.n_floors)]}}
            # By default, expect 1 button press per floor every hour.
        return

    def set_expected_destinations(self, val=None, weekdays=None, timestamp=None, floors=None):
        """
        Sets the expected values for button presses in the building per hour

        Arguments:
        val -- The value to insert into the expected_destinations dict at the location specified by the other args. Can be a full dict, a list, or just a value. 
        weekdays -- Optional, list of days of the week this schedule is being applied to. If unspecified, sets the default value (Used for all weekdays that arent already set)
        timestamp -- Optional, the time of day this schedule begins at. If left blank, clears all other times and sets new one to start at "0000" (active all day) 
        floors -- Optional, list of floors to apply the new hourly rate to. If left blank, applies to all floors.
        """
        return

    def spawn_person(self):
        # self.building.add_waiting_person(self)
        pass
