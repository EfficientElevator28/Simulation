"""
Author: Daniel Nichols
"""
from src.ElevatorState import ElevatorState


class Elevator:
    """
    Elevator class.
    """

    def __init__(self, name, max_velocity=2.5, max_acc=1, jerk=0, speed=0, avg_boarding_time=5, max_riders=10,
                 init_position=0.0):
        """
        inits the elevator.

        Parameters:
        name -- name of this elevator
        speed -- elevator speed in floors/sec
        avg_boarding_time -- average time spent at each floor (factors in door closing/opening)
        max_velocity -- maximum elevator velocity
        max_acc -- max elevator acceleration
        jerk -- elevator jerk (derivative of acceleration)
        max_riders -- maximum personnel allowed on elevator
        position -- distance (in meters) above the base of floor 1; used by simulation for positioning
        """
        self.name = name
        # self.building = building -- chicken in egg kind of:
        # (building takes elevators as param, elevator takes building as param)
        self.speed = speed
        self.avg_boarding_time = avg_boarding_time
        self.max_velocity = max_velocity
        self.max_acc = max_acc
        self.jerk = jerk
        self.max_riders = max_riders
        self.position = init_position
        self.state = ElevatorState.NO_ACTION
        # TODO: Elevator should have a list of floors it is requested to stop on to determine order of events
        #       For people inside the elevator, their destination should be added to this list when they are added
        #       For people waiting for an elevator, the building should decide which elevator is best situated to pick them up,
        #               and add their floor to that elevator's requests.
        self.queued_floors = []
        self.riders = []


    def step(self, building, dt):
        """
        step the elevator forward.
        """

        if self.state == ElevatorState.UP:
            # use constant speed
            self.position += self.velocity * dt
            
            # check if past desired floor
            cur_floor = building.get_floor_by_position(self.position)
            next_floor = self.queued_floors[0]

            if cur_floor.floor_number == next_floor.floor_number:
                print('at correct floor')
                self.state = ElevatorState.LOADING_UNLOADING

                # clamp the position
                self.position = building.get_position_of_floor(next_floor)

                # remove floor from queue
                self.queued_floors.pop(0)

        elif self.state == ElevatorState.DOWN:
            # adjust with constant speed
            self.position -= self.velocity * dt

            # check if below desired floor
            cur_floor = building.get_floor_by_position(self.position)
            next_floor = self.queued_floors[0]

            if cur_floor.floor_number == next_floor.floor_number:
                print('at correct floor; down')
                self.state = ElevatorState.LOADING_UNLOADING
                
                # clamp elevator position
                self.position = building.get_position_of_floor(next_floor)

                # remove floor from list
                self.queued_floors.pop(0)

            
        elif self.state == ElevatorState.LOADING_UNLOADING:
            # handle loading/unloading
            pass
        elif self.state == ElevatorState.NO_ACTION:
            # do nothing bitch
            pass


        return None

    def add_rider(self, rider):
        '''
        Adds a rider to the elevator cart.
        Returns -1 and does nothing if rider is None.
        Returns rider index otherwise.
        '''
        if rider is None:
            return -1

        self.riders.append(rider)
        # TODO: See todo in __init__ - rider destination should be added to the list of requested stops
        return len(self.riders)-1

    def remove_rider(self, rider):
        '''
        Removes the rider from the rider list.
        Returns the new size of the rider list.
        '''
        if rider is None:
            return -1

        if rider in self.riders:
            self.riders.remove(rider)

    def get_num_riders(self):
        '''
        Get the number of riders.
        '''
        return len(self.riders)


    def press_up_button(self):
        """
        Simulate a user pressing the UP button.
        """