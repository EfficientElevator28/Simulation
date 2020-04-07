from src.Person import Person
from src.PersonScheduler import *
from src.Visualization.visualization import Visualization
from src.simulator import *
from src.building import *
from src.elevator import *
import time
import pyglet as pyglet


def run_rl_v1_test():
    sim = Simulator('RL_V1', step_func=realistic_physics_step_func, reward_func=reward_sum_people,
                    rl_step_func=rl_step_func_v1)
    elevators = [Elevator(1)]
    building = Building(name=1, elevators=elevators, n_floors=10)
    sim.init_building(building)
    vis = Visualization(building)

    # The person_scheduler is only externally dependent on the starting_time which is fed to the rl_step in the
    # simulation.
    # Note: poisson_mean_density=.2 (means average spawn .2 people per second), seconds_to_schedule=100000 (don't
    # exceed this system time which is tracked in sim.total_time).
    person_scheduler = PersonScheduler(building, poisson_mean_density=.05, seconds_to_schedule=100000)
    print(person_scheduler.people_spawning[:10])

    # Custom event loop which dispatches an on_draw event, which updates the screen to the current state
    vis.pyglet_window.dispatch_event("on_draw")
    while vis.alive == 1:
        print("Total Time Elapsed: " + str(sim.total_time) + "; Running draw events...")

        # Optional: insert sleep time to slow down the simulation; if so, press ESC on keyboard to exit visualization
        time.sleep(2)

        # These three lines are needed for the visualization - don't edit
        pyglet.clock.tick()
        vis.pyglet_window.dispatch_events()
        vis.pyglet_window.dispatch_event("on_draw")

        # Carl's RL code goes here - the code under the comment "Run simulation step" can serve as an template/example
        # of what to run to progress the simulation w/ a given action.
        # However, note that the simulator object (sim) contains the reference to the building and therefore the
        # elevators, floors, people, etc. Thus, if the reinforcement learning wants to test multiple actions to see the
        # reward outputs, you will need to make a DEEP COPY of sim so that you aren't using another sim's references.
        # You shouldn't make copies of the simulation or the person_scheduler, as I designed the person_scheduler to
        # give the same output (seeded) and internally, it only accepts a time (presumably sim.total_time).
        # ...
        # ...

        # Run simulation step
        # See bottom of file for more example code if you want to see the elevator move...
        starting_time = sim.total_time
        action = 8  # floor to put the single elevator on (currently only does anything if people are in the system)
        state_list, reward, bld = sim.rl_step(starting_time=starting_time, action=action,
                                              person_scheduler=person_scheduler)


if __name__ == '__main__':
    run_rl_v1_test()


"""
# Examples of how it works - paste into while loop under the visualization 3 lines
        if sim.total_time > 50 and building.elevators[0].state == ElevatorState.NO_ACTION:
            starting_time = sim.total_time
            action = 4  # floor to put the single elevator on (currently only does anything if people are in the system)
            state_list, reward, bld = sim.rl_step(starting_time=starting_time, action=action,
                                                  person_scheduler=person_scheduler)
        elif sim.total_time > 10 and building.elevators[0].state == ElevatorState.NO_ACTION:
            starting_time = sim.total_time
            action = 5  # floor to put the single elevator on (currently only does anything if people are in the system)
            state_list, reward, bld = sim.rl_step(starting_time=starting_time, action=action,
                                                  person_scheduler=person_scheduler)
        else:
            # Run simulation step
            starting_time = sim.total_time
            action = 8  # floor to put the single elevator on (currently only does anything if people are in the system)
            state_list, reward, bld = sim.rl_step(starting_time=starting_time, action=action,
                                                  person_scheduler=person_scheduler)
"""