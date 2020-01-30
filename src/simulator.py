"""
author: Daniel Nichols
"""


class Simulator:
    """
    Simulator class.
    """

    def __init__(self, name, step_func):
        """
        initialize the Simulator.
        """
        self.name = name
        self.step_func = step_func

    def step(self):
        """
        step the Simulator forward
        """
        return self.step_func()

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

