"""
author: Daniel Nichols
"""


def default_step_func(cur_building, dt):
    """
    A default version of the step function.
    """

    # step each elevator forward
    for e in cur_building.elevators:
        e.step(cur_building, dt)

    # now adjust all the people
    # TODO get the people parameter form elevator

    return True


def realistic_physics_step_func(cur_building, time_inc):
    """
    Step function which uses realistic physics calculations/movements
    """
    print("step func called")
    # Update position and passengers of elevators (and floors if there is any loading/unloading done
    for e in cur_building.elevators:
        # Elevator class's step_realistic_physics...
        e.step_realistic_physics(cur_building, time_inc)

        # Update wait times of elevator riders
        for person in e.riders:
            person.wait_time += time_inc

    # Update the waiting time of people on floors still
    for floor in cur_building.floors:
        for person in floor.people_waiting:
            person.wait_time += time_inc

    return True


class Simulator:
    """
    Simulator class.
    """

    def __init__(self, name, step_func=default_step_func):
        """
        initialize the Simulator.
        """
        self.name = name
        self.step_func = step_func

    def init_building(self, building):
        self.building = building

    def step(self, dt=1.0):
        """
        step the Simulator forward
        """

        if self.building is None:
            print('Building not initialized')
            return None

        return self.step_func(self.building, dt)

    def run(self, timestep=1, new_thread=False):
        """
        run the simulator
        """
        self._running = True
        self._run()

    def _run(self):
        """
        Internal func.
        """
        while self._running:
            self._running = self.step()

