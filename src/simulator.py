"""
author: Daniel Nichols
"""

def default_step_func(cur_building):

    for e in cur_building.elevators:
        # step the current elevator e
        pass

    # now adjust all the people
    # TODO get the people parameter form elevator

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

    def step(self):
        """
        step the Simulator forward
        """
        return self.step_func(self.buiding)

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

