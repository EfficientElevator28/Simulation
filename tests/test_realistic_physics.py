from src.Person import Person
from src.Visualization.visualization import Visualization
from src.simulator import *
from src.building import *
from src.elevator import *
import time
import pyglet as pyglet


def run_realistic_physics_test():
    sim = Simulator('Realistic Sim', step_func=realistic_physics_step_func)
    elevators = [Elevator(1), Elevator(2), Elevator(3), Elevator(4)]
    building = Building(name=1, elevators=elevators, n_floors=10)
    sim.init_building(building)
    vis = Visualization(building)

    # Setup people waiting on a floor who need to get off at other floors. Also, add destinations for the elevator #1
    elevators[1].queued_floors.append(building.floors[1])
    elevators[1].queued_floors.append(building.floors[4])
    elevators[1].queued_floors.append(building.floors[7])
    elevators[1].queued_floors.append(building.floors[6])
    # 3 people get on @ floor 2.
    # At floor 4, 2 people get off and 3 get on - 4 total now
    # At floor 7, 3 people get off and 1 gets on (only b/c floor below him/her is queued) - 1 total now
    building.floors[1].up_pressed = True
    building.floors[4].up_pressed = True
    building.floors[7].down_pressed = True

    building.floors[1].people_waiting.append(Person(floor=1, destination=4))
    building.floors[1].people_waiting.append(Person(floor=1, destination=4))
    building.floors[1].people_waiting.append(Person(floor=1, destination=7))
    building.floors[4].people_waiting.append(Person(floor=4, destination=7))
    building.floors[4].people_waiting.append(Person(floor=4, destination=7))
    building.floors[4].people_waiting.append(Person(floor=4, destination=7))
    building.floors[7].people_waiting.append(Person(floor=7, destination=3))

    # Custom event loop which dispatches an on_draw event, which updates the screen to the current state
    vis.pyglet_window.dispatch_event("on_draw")
    while vis.alive == 1:
        # print("Running loop")
        time.sleep(5)

        # These three lines are needed
        pyglet.clock.tick()
        vis.pyglet_window.dispatch_events()
        vis.pyglet_window.dispatch_event("on_draw")

        # Run simulation step
        sim.step(1.0)
        if len(elevators[1].queued_floors) > 0:
            print("Next floor: " + str(elevators[1].queued_floors[0].floor_number))

        '''building.elevators[0].position += 3
        building.elevators[2].position += 2
        building.elevators[0].state = ElevatorState.LOADING_UNLOADING
        building.elevators[1].state = ElevatorState.UP
        building.elevators[2].state = ElevatorState.DOWN
        building.elevators[3].state = ElevatorState.NO_ACTION'''


if __name__ == '__main__':
    run_realistic_physics_test()