"""
author: Daniel Nichols
"""
from src.ElevatorState import ElevatorState


def default_step_func(cur_building, dt):
    """
    DEFUNCT - A default version of the step function.
    """

    # step each elevator forward
    for e in cur_building.elevators:
        e.step(cur_building, dt)

    # now adjust all the people
    # DEFUNCT TODONT get the people parameter form elevator

    return True


def rl_step_func_v1(cur_building, starting_time, time_inc, action, person_scheduler):
    """
    Reinforcement learning step function does the following:
    1) add the action
    2a) If elevator’s state is NO_ACTION and no people in system, progress until a floor is pressed.
    2b) Else, call step func (calls realistic_physics_step_func (with abbr_step_option=True)) and queue people as
    needed until there is no longer a queued elevator.

    Note: this is for a one elevator system ONLY.
    Note: cur_building and the internal elevator need to be a deep copy

    action -- destination floor for the single elevator system
    """

    # First: implement the action: add the floor we are going to to the single elevator's queued_floors member
    cur_building.elevators[0].queued_floors.append(cur_building.floors[action])

    # Second: IF elevator’s state is NO_ACTION and no people in system, progress until a floor is pressed
    current_time = starting_time

    if cur_building.elevators[0].state == ElevatorState.NO_ACTION and cur_building.get_total_people_in_system() == 0:
        next_spawn_time, people_to_spawn = person_scheduler.get_time_and_people_of_next_addition(
            current_timestamp=current_time)
        person_scheduler.spawn_people(next_spawn_time, people_to_spawn)
        return

    # Second: ELSE, call step func and queue people as needed until there is no longer a queued elevator
    while len(cur_building.elevators[0].queued_floors) > 0:
        next_spawn_time, people_to_spawn = person_scheduler.get_time_and_people_of_next_addition(
            current_timestamp=current_time)
        time_till_next_spawn = next_spawn_time - current_time

        if time_till_next_spawn < time_inc:
            # People are going to spawn before the standard time_inc can be elapsed
            return_cond, actual_time_inc = realistic_physics_step_func(cur_building, time_till_next_spawn,
                                                                       abbr_step_option=True)
            if actual_time_inc == time_till_next_spawn:
                # Implies loading/unloading didn't finish early
                person_scheduler.spawn_people(next_spawn_time, people_to_spawn)
        else:
            return_cond, actual_time_inc = realistic_physics_step_func(cur_building, time_inc, abbr_step_option=True)


def realistic_physics_step_func(cur_building, time_inc, abbr_step_option=False):
    """
    Step function which uses realistic physics calculations/movements
    abbr_step_option -- If abbr_step_option is set to True, the elevators will only continue to the point where an
    elevator is done loading/unloading. This is a custom option used by some RL step functions.
    """
    # print("step func called")

    new_time_inc = time_inc
    if abbr_step_option:
        # Change new_time_inc to where an elevator is done with its loading/unloading
        for e in cur_building.elevators:
            boarding_time_remaining = e.avg_boarding_time - e.time_since_beg_of_action
            if e.state == ElevatorState.LOADING_UNLOADING and boarding_time_remaining < new_time_inc:
                new_time_inc = boarding_time_remaining + .0001  # Account for rounding error

    # Update position and passengers of elevators (and floors if there is any loading/unloading done
    for e in cur_building.elevators:
        # Elevator class's step_realistic_physics...
        e.step_realistic_physics(cur_building, new_time_inc)

        # Update wait times of elevator riders
        for person in e.riders:
            person.wait_time += new_time_inc

    # Update the waiting time of people on floors still
    for floor in cur_building.floors:
        for person in floor.people_waiting:
            person.wait_time += new_time_inc

    return True, new_time_inc


# Default reward function -- returns -(sum # people) where # people includes those waiting for and on elevators
def reward_sum_people(cur_building):
    sum_people = 0
    for e in cur_building.elevators:
        if e.riders is not None:
            sum_people += len(e.riders)
    for floor in cur_building.floors:
        if floor.people_waiting is not None:
            sum_people += len(floor.people_waiting)
    return -sum_people


class Simulator:
    """
    Simulator class.
    """

    def __init__(self, name, step_func=default_step_func, reward_func=reward_sum_people):
        """
        initialize the Simulator.
        """
        self.name = name
        self.total_time = 0  # total time elapsed
        self.step_func = step_func
        self.reward_func = reward_func

    def init_building(self, building):
        self.building = building

    def reward(self):
        return self.reward_func(self.building)

    def step(self, dt=1.0):
        """
        step the Simulator forward
        """

        if self.building is None:
            print('Building not initialized')
            return None

        self.total_time += dt
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

    def get_state(self):
        """
        Creates a list of state variables which go into a list that will be used to calculate a reward
        Returns -- tuple of (building, state list)
        """
        states = []

        # For each elevator, and for each floor, add a 0/1 for a floor button press
        for elevator in self.building.elevators:
            dest_floors_dict = dict()
            for rider in elevator.riders:
                dest_floors_dict[rider.destination] = dest_floors_dict.get(rider.destination, 0) + 1
            for floor in self.building.floors:
                states.append(dest_floors_dict.get(floor.floor_number, 0))

        # Add up/down button presses for outside each floor
        for floor in self.building.floors:
            states.append(int(floor.up_pressed is True))
            states.append(int(floor.down_pressed is True))

        # Add numbers of people waiting outside of each floor
        for floor in self.building.floors:
            if floor.people_waiting is not None:
                states.append(len(floor.people_waiting))
            else:
                states.append(0)

        return self.building, states

