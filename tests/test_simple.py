from src.simulator import *
from src.building import *
from src.elevator import *


def test_simulation():
    sim = Simulator('default_simulator')

    e1 = Elevator('elevator_1')
    e2 = Elevator('elevator_2')
    elevators = [e1, e2]

    building = Building('default_building', elevators, 5)

    sim.init_building(building)

    sim.step()

    e2.press_up_button()


    sim.step()

def run_tests():
    test_simulation()


if __name__ == '__main__':
    run_tests()