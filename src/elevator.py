"""
Author: Daniel Nichols
"""
from src.ElevatorState import ElevatorState
from src.elevator_motion import ElevatorMotion
from src.building import Building
from math import sqrt


class Elevator:
    """
    Elevator class.
    """

    def __init__(self, name, max_velocity=2.5, max_acc=1, max_dec=-0.5, jerk=0, velocity=0, avg_boarding_time=5,
                 max_riders=10, init_position=0.0, time_since_beg_of_action=0.0):
        """
        inits the elevator.

        Parameters:
        name -- name of this elevator
        velocity -- elevator velocity in floors/sec
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
        self.velocity = velocity
        self.avg_boarding_time = avg_boarding_time
        self.max_velocity = max_velocity  # 2.2-10 m/s
        self.max_acc = max_acc  # between 1-1.2 m/s^2 relative to direction of travel
        self.max_dec = max_dec  # set to -0.5 m/s^2 relative to direction of travel
        self.prev_acc_dec = ElevatorMotion.NEITHER
        self.jerk = jerk  # not used, assuming constant acceleration
        self.max_riders = max_riders
        self.position = init_position
        self.time_since_beg_of_action = time_since_beg_of_action
        self.state = ElevatorState.NO_ACTION
        self.time_to_stop_from_max_velocity = self.calc_time_to_reach_velocity(0, max_velocity, max_dec)
        self.dist_to_stop_from_max_velocity = self.calc_distance_per_time(max_velocity, max_dec,
                                                                          self.time_to_stop_from_max_velocity)
        # TODO: Elevator should have a list of floors it is requested to stop on to determine order of events
        #       For people inside the elevator, their destination should be added to this list when they are added
        #       For people waiting for an elevator, the building should decide which elevator is best situated to pick them up,
        #               and add their floor to that elevator's requests.
        self.queued_floors = []
        self.riders = []

    def physics_calc(self, building, total_time_increment):
        """
        Calculate distance traveled and time remaining (which will contribute to time_since_beg_of_action).
        This is the only function that updates ElevatorState to UP or DOWN
        """
        time_threshold = .02
        dist_threshold = .02

        # Calculate remaining distance to travel to get to desired floor
        desired_floor_num = self.queued_floors[0].floor_number
        desired_floor_height = desired_floor_num * building.floor_dist  # floor 0 at height 0
        total_remaining_dist = abs(self.position - desired_floor_height)
        if self.position < desired_floor_height:
            direction_of_travel = "up"
            self.state = ElevatorState.UP
        else:
            direction_of_travel = "down"
            self.state = ElevatorState.DOWN

        # If prev_acc_dec is GETTING_FASTER,
        # or if it is NEITHER and time_since_beg_of_action is zero (so it hasn't started moving)
        if self.prev_acc_dec == ElevatorMotion.GETTING_FASTER or \
                (self.prev_acc_dec == ElevatorMotion.NEITHER and self.time_since_beg_of_action < time_threshold):
            # Determine if elevator can accelerate to max velocity and decelerate to velocity=0 in remaining distance
            print("Getting faster")
            if direction_of_travel == "up":
                time_to_reach_max_velocity = self.calc_time_to_reach_velocity(self.max_velocity, self.velocity,
                                                                              self.max_acc)
            else:  # down
                time_to_reach_max_velocity = self.calc_time_to_reach_velocity(-self.max_velocity, self.velocity,
                                                                              -self.max_acc)
            dist_covered_to_reach_max_velocity = self.calc_distance_per_time(abs(self.velocity), self.max_acc,
                                                                             time_to_reach_max_velocity)
            dist_to_max_and_stop = dist_covered_to_reach_max_velocity + self.dist_to_stop_from_max_velocity
            if dist_to_max_and_stop <= total_remaining_dist:
                # Elevator can hit max velocity in remaining distance
                new_position, time_remaining = \
                    self.speeding_up_calc_dist_time(total_time_increment, v1=self.velocity, a1=self.max_acc,
                                                    a2=self.max_dec, starting_position=self.position,
                                                    desired_position=desired_floor_height,
                                                    total_remaining_dist=total_remaining_dist)
                return new_position, time_remaining
            else:
                # Elevator won't hit max velocity in remaining distance
                print("Running abbreviated speed up/slow down")
                if direction_of_travel == "up":
                    new_position, time_remaining = \
                        self.abbr_velocity_calc_dist_time(total_time_increment, d0=self.position, v1=self.velocity,
                                                          a1=self.max_acc, s0=desired_floor_height, a2=self.max_dec)
                else:
                    new_position, time_remaining = \
                        self.abbr_velocity_calc_dist_time(total_time_increment, d0=self.position, v1=self.velocity,
                                                          a1=-self.max_acc, s0=desired_floor_height, a2=-self.max_dec)
                return new_position, time_remaining
        # If prev_acc_dec is NEITHER -- maybe can cover in previous case since time to accelerate to max velocity is 0
        # Case: velocity is non-zero and no current acceleration/deceleration
        elif self.prev_acc_dec == ElevatorMotion.NEITHER:
            print("Neither")
            new_position, time_remaining = \
                self.constant_rate_calc_dist_time(total_time_increment, v2=self.velocity, a2=self.max_dec,
                                                  starting_position=self.position,
                                                  desired_position=desired_floor_height,
                                                  total_remaining_dist=total_remaining_dist)
            return new_position, time_remaining
        # If prev_acc_dec is SLOWING
        else:
            print("Slowing")
            new_position, time_remaining = \
                self.slowing_down_calc_dist_time(total_time_increment, v2=self.velocity, a2=self.max_dec,
                                                 starting_position=self.position, desired_position=desired_floor_height)
            return new_position, time_remaining

    def speeding_up_calc_dist_time(self, time_increment, v1, a1, a2, starting_position, desired_position,
                                   total_remaining_dist):
        time_req_hit_max_speed = (abs(self.max_velocity) - abs(v1)) / abs(a1)
        dist_req_hit_max_speed = self.calc_distance_per_time(abs(v1), abs(a1), time_req_hit_max_speed)

        if time_req_hit_max_speed > time_increment:
            # Not enough time left to hit max speed
            self.prev_acc_dec = ElevatorMotion.GETTING_FASTER
            adjusted_distance_change = self.calc_distance_per_time(abs(v1), abs(a1), time_increment)

            # Update velocity
            if self.velocity > 0:
                self.velocity += abs(a1) * time_increment
            else:
                self.velocity -= abs(a1) * time_increment

            if starting_position < desired_position:
                return (starting_position + adjusted_distance_change), 0.0
            else:
                return (starting_position - adjusted_distance_change), 0.0
            pass
        else:
            # Enough time left to hit max speed
            self.prev_acc_dec = ElevatorMotion.NEITHER

            # Update velocity - used when calculating distance with constant rate (the new rate)
            if self.velocity > 0:
                self.velocity += abs(a1) * time_req_hit_max_speed
            else:
                self.velocity -= abs(a1) * time_req_hit_max_speed

            if starting_position < desired_position:
                return self.constant_rate_calc_dist_time(time_increment - time_req_hit_max_speed, self.max_velocity, a2,
                                                         starting_position + dist_req_hit_max_speed, desired_position,
                                                         total_remaining_dist - dist_req_hit_max_speed)
            else:
                return self.constant_rate_calc_dist_time(time_increment - time_req_hit_max_speed, self.max_velocity, a2,
                                                         starting_position - dist_req_hit_max_speed, desired_position,
                                                         total_remaining_dist - dist_req_hit_max_speed)

    def constant_rate_calc_dist_time(self, time_increment, v2, a2, starting_position, desired_position,
                                     total_remaining_dist):
        time_req_to_stop = abs(v2 / a2)
        dist_req_to_stop = self.calc_distance_per_time(abs(v2), -abs(a2), time_req_to_stop)  # > total_remaining_dist

        dist_at_constant_rate = total_remaining_dist - dist_req_to_stop
        time_at_constant_rate = abs(dist_at_constant_rate / v2)

        # Check if the remaining time is going to be spend completely at constant rate
        if time_at_constant_rate > time_increment:
            # Case: remaining time doesn't allow the elevator to start slowing down
            # ElevatorMotion remains set to NEITHER
            adjusted_distance_change = abs(v2 * time_increment)
            if starting_position < desired_position:
                return (starting_position + adjusted_distance_change), 0.0
            else:
                return (starting_position - adjusted_distance_change), 0.0
        else:
            # Case: remaining time allows elevator to start slowing down
            # ElevatorMotion is adjusted in called method
            if starting_position < desired_position:
                return self.slowing_down_calc_dist_time(time_increment - time_at_constant_rate, v2, a2,
                                                        starting_position + dist_at_constant_rate, desired_position)
            else:
                return self.slowing_down_calc_dist_time(time_increment - time_at_constant_rate, v2, a2,
                                                        starting_position - dist_at_constant_rate, desired_position)

    def slowing_down_calc_dist_time(self, time_increment, v2, a2, starting_position, desired_position):
        # The remaining distance (abs(starting_position - desired_position)) should match up with the time_req_to_stop
        # because of how other funcs work.
        # Based off the acc/vel, we know the time needed to stop. So, comparing this with the time_increment remaining,
        # we can know if/what the leftover time is.
        time_req_to_stop = abs(v2 / a2)
        if time_req_to_stop < time_increment:
            self.velocity = 0.0
            self.prev_acc_dec = ElevatorMotion.NEITHER
            return desired_position, (time_increment - time_req_to_stop)
        else:
            dist_covered_in_remaining_time = self.calc_distance_per_time(abs(v2), -abs(a2), time_increment)

            # Update velocity
            if starting_position < desired_position:
                self.velocity -= abs(a2) * time_increment
            else:
                self.velocity += abs(a2) * time_increment

            if starting_position < desired_position:
                ending_position = starting_position + dist_covered_in_remaining_time
            else:
                ending_position = starting_position - dist_covered_in_remaining_time
            self.prev_acc_dec = ElevatorMotion.SLOWING
            return ending_position, 0.0

    # For speeding up, but not going to hit max speed
    def abbr_velocity_calc_dist_time(self, time_increment, d0, v1, a1, s0, a2):
        """
        Determines the total distance covered and remaining time in the case of the elevator not being able to reach
        its max_velocity. Also, updates prev_acc_dec as needed.
        Returns -- tuple of ending position and remaining time (leftover time to count towards the loading/unloading;
        remaining time is only > 0 when the elevator's initially still speeding up and it manages to stop in the
        time_increment or else this function would never have been reached)
        """
        # d0 is starting position
        # v1 is current velocity (directional)
        # a1 is the max speeding up acceleration (take max_acc and keep positive for direction_of_travel "up" and make
        #   negative for direction_of_travel "down")
        # s0 is the target floor's position
        # v2 (not shown) is 0 (starting velocity coming from the other direction)
        # a2 is the max slowing down acceleration (take max_dec and keep negative for direction_of_travel "up" and make
        #   positive for direction_of_travel "down")
        # quad_a = (a1 * a1 / 2 / a2) - (a1 / 2)
        # quad_b = v1 * a1 / a2 - v1
        # quad_c = (v1 * v1 / 2 / a2) + s0 - d0
        print("d0=" + str(d0) + " s0=" + str(s0) + " v1=" + str(v1) + " a1=" + str(a1) + " a2=" + str(a2))

        quad_a = abs(a1)/2 + abs(a1)*abs(a1)/2/abs(a2)
        quad_b = abs(v1) + abs(a1)*abs(v1)/abs(a2)
        quad_c = -abs(abs(d0) - abs(s0)) + abs(v1)*abs(v1)/2/abs(a2)
        print("Quadratic params: a=" + str(quad_a) + " b=" + str(quad_b) + " c=" + str(quad_c))

        # larger < 0 might indicate no remaining time
        q_success, larger, smaller = self.quadratic_formula(quad_a, quad_b, quad_c)
        print("Quadratic - larger=" + str(larger) + ", smaller=" + str(smaller))
        remaining_time_to_increase_acc = max(larger, 0.0)  # aka t1

        if time_increment < remaining_time_to_increase_acc:
            # Solve for distance traveled in terms of time_increment and return; this works since the time remaining
            # in the step is not enough to reach our smaller target velocity (which is optimized to minimize time)
            abbr_distance_covered_speeding_up = self.calc_distance_per_time(abs(v1), abs(a1), time_increment)
            # Depending on direction of travel, return the correct ending position
            self.prev_acc_dec = ElevatorMotion.GETTING_FASTER

            # Update velocity
            if self.velocity == 0.0:
                if d0 < s0:
                    self.velocity += abs(a1) * time_increment
                else:
                    self.velocity -= abs(a1) * time_increment
            elif self.velocity > 0:
                self.velocity += abs(a1) * time_increment
            else:
                self.velocity -= abs(a1) * time_increment

            if d0 < s0:
                return (d0 + abbr_distance_covered_speeding_up), 0.0
            else:
                return (d0 - abbr_distance_covered_speeding_up), 0.0
        else:
            # Calculate distance covered over entire remaining_time_to_increase_acc when speeding up
            distance_covered_speeding_up = self.calc_distance_per_time(abs(v1), abs(a1), remaining_time_to_increase_acc)

            # Because we know what remaining_time_to_increase_acc is we can calculate the highest velocity hit
            time_remaining_after_hitting_final_velocity = time_increment - remaining_time_to_increase_acc
            positive_final_velocity_at_end_t1 = abs(v1) + abs(a1) * remaining_time_to_increase_acc

            # Need to calc if we have leftover time
            time_needed_to_slow_down = positive_final_velocity_at_end_t1 / abs(a2)
            if time_needed_to_slow_down < time_remaining_after_hitting_final_velocity:
                # There will be leftover time
                leftover_time = time_remaining_after_hitting_final_velocity - time_needed_to_slow_down
                time_used_to_slow_down = time_remaining_after_hitting_final_velocity - time_needed_to_slow_down
                distance_covered_slowing_down = self.calc_distance_per_time(positive_final_velocity_at_end_t1, -abs(a2),
                                                                            time_used_to_slow_down)
                # total dist = distance_covered_speeding_up + distance_covered_slowing_down
                self.prev_acc_dec = ElevatorMotion.NEITHER

                # Update velocity
                self.velocity = 0.0

                return s0, leftover_time
            else:
                # There is no leftover time: the desired floor/distance isn't reached
                abbr_distance_covered_slowing_down = \
                    self.calc_distance_per_time(positive_final_velocity_at_end_t1, -abs(a2),
                                                time_remaining_after_hitting_final_velocity)
                total_dist_covered = distance_covered_speeding_up + abbr_distance_covered_slowing_down
                self.prev_acc_dec = ElevatorMotion.SLOWING

                # Update velocity
                new_velocity = positive_final_velocity_at_end_t1 - abs(a2) * time_remaining_after_hitting_final_velocity
                if d0 < s0:  # going up
                    self.velocity = new_velocity
                else:  # going down
                    self.velocity = -new_velocity

                if d0 < s0:
                    return (d0 + total_dist_covered), 0.0
                else:
                    return (d0 - total_dist_covered), 0.0

    @staticmethod
    # Calculates distance covered over a time, not a final position
    def calc_distance_per_time(initial_velocity, acceleration, time):
        return abs(initial_velocity * time + .5 * acceleration * time * time)

    @staticmethod
    def calc_time_to_reach_velocity(desired_velocity, current_velocity, acc_dec):
        return (desired_velocity - current_velocity) / acc_dec

    def calc_time_to_reach_distance(self, initial_position, final_position, initial_velocity, acc_dec):
        a = .5 * acc_dec
        b = initial_velocity
        c = initial_position - final_position
        q_success, larger, smaller = self.quadratic_formula(a, b, c)
        if larger < 0:
            print("Error: calc_time_to_reach_distance would return time less than 0")
        return max(larger, 0.0)

    @staticmethod
    def quadratic_formula(a, b, c):
        under_radical = b * b - 4 * a * c
        if under_radical < 0.0:
            print("Quadratic negative under radical: a=" + str(a) + " b=" + str(b) + " c=" + str(c))
            return False, 0, 0
        radical = sqrt(under_radical)
        ans1 = (-b + radical) / (2 * a)
        ans2 = (-b - radical) / (2 * a)
        if ans1 > ans2:
            return True, ans1, ans2
        return True, ans2, ans1

    def load_unload(self, desired_floor_num, building, time_remaining, time_inc):
        # Person.destination and Elevator.max_riders determine if a rider gets on/off
        desired_floor = building.floors[desired_floor_num]

        # Unload passengers first - may open up more capacity. Iterate backwards to be able to remove riders
        for rider_index in range(self.get_num_riders() - 1, -1, -1):
            rider = self.riders[rider_index]
            if rider.destination == desired_floor_num:
                rider.waiting_state = 0
                rider.wait_time += time_inc - time_remaining
                self.remove_rider_index(rider_index)

        # Load passengers
        if len(self.queued_floors) > 1:
            next_floor_num = self.queued_floors[1].floor_number
            if next_floor_num < desired_floor_num:
                desired_floor.down_pressed = False
            else:
                desired_floor.up_pressed = False

            # Create list of rider (indexes) to transfer from the floor to the elevator
            rider_indexes_to_transfer = []
            for rider_num in range(0, len(desired_floor.people_waiting)):
                if next_floor_num > desired_floor_num and \
                        desired_floor.people_waiting[rider_num].destination > desired_floor_num:
                    rider_indexes_to_transfer.append(rider_num)
                elif next_floor_num < desired_floor_num and \
                        desired_floor.people_waiting[rider_num].destination < desired_floor_num:
                    rider_indexes_to_transfer.append(rider_num)

            rider_indexes_transferred = []
            if len(rider_indexes_to_transfer) > 0:
                for rider_num in range(0, min(len(rider_indexes_to_transfer), self.max_riders - self.get_num_riders())):
                    # Add rider to the elevator
                    rider_indexes_transferred.append(rider_num)
                    desired_floor.people_waiting[rider_num].waiting_state = -1
                    self.riders.append(desired_floor.people_waiting[rider_num])

            if len(rider_indexes_transferred) > 0:
                # Remove rider from the floor. Do in reverse order since popping.
                for rider_num in range(len(rider_indexes_transferred) - 1, -1, -1):
                    desired_floor.people_waiting.pop(rider_num)

        # Loading/unloading done, so remove floor from elevator's queued_floors
        self.queued_floors.pop(0)

    def physics_calc_changes(self, new_position, time_remaining, distance_threshold, desired_floor_height,
                             desired_floor_num, time_inc, building):
        if abs(new_position - desired_floor_height) < distance_threshold:
            # The elevator arrived at the requested floor
            self.position = desired_floor_height
            self.prev_acc_dec = ElevatorMotion.NEITHER

            # Run loading/unloading procedure - pop off the floor and move the people (on & off)
            self.load_unload(desired_floor_num, building, time_remaining, time_inc)

            self.state = ElevatorState.LOADING_UNLOADING
            self.time_since_beg_of_action = time_remaining
        else:
            # The elevator has not yet arrived at the requested floor
            self.position = new_position
            self.time_since_beg_of_action += time_inc

    def step_realistic_physics(self, building, time_inc):
        """
        time_inc must be less than the avg_boarding_time to work
        Note: if there are no queued elevators, it is set to currently not move.
        """
        distance_threshold = .01
        print("--------")
        # If elevator is idle but queued_floors has now been updated, change state in order to perform an action
        if self.state == ElevatorState.NO_ACTION:
            if len(self.queued_floors) > 0:
                desired_floor_num = self.queued_floors[0].floor_number
                desired_floor_height = desired_floor_num * building.floor_dist  # floor 0 at height 0

                if self.position > desired_floor_height:
                    self.state = ElevatorState.DOWN
                    self.time_since_beg_of_action = 0
                else:
                    self.state = ElevatorState.UP
                    self.time_since_beg_of_action = 0
            pass

        if self.state == ElevatorState.UP or self.state == ElevatorState.DOWN:
            if len(self.queued_floors) > 0:
                desired_floor_num = self.queued_floors[0].floor_number
                desired_floor_height = desired_floor_num * building.floor_dist  # floor 0 at height 0

                new_position, time_remaining = self.physics_calc(building, time_inc)
                print("UP/DOWN - Current position: " + str(self.position) + ", new position: " + str(new_position))
                self.physics_calc_changes(new_position, time_remaining, distance_threshold, desired_floor_height,
                                          desired_floor_num, time_inc, building)
            else:
                self.state = ElevatorState.NO_ACTION
        elif self.state == ElevatorState.LOADING_UNLOADING:
            # People are already considered loaded/unloaded if the step func is starting in this state
            loading_time_remaining = self.avg_boarding_time - self.time_since_beg_of_action
            if time_inc < loading_time_remaining:
                self.time_since_beg_of_action += time_inc
            else:
                self.time_since_beg_of_action = 0
                if len(self.queued_floors) > 0:
                    desired_floor_num = self.queued_floors[0].floor_number
                    desired_floor_height = desired_floor_num * building.floor_dist  # floor 0 at height 0

                    movement_time_remaining = loading_time_remaining - time_inc
                    new_position, time_remaining = self.physics_calc(building, movement_time_remaining)
                    self.physics_calc_changes(new_position, time_remaining, distance_threshold, desired_floor_height,
                                              desired_floor_num, time_inc, building)
                else:
                    self.time_since_beg_of_action = 0
                    self.state = ElevatorState.NO_ACTION
                pass
        else:  # ElevatorState.NO_ACTION
            pass
        return None

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

    def remove_rider_index(self, rider_index):
        self.riders.pop(rider_index)

    def get_num_riders(self):
        '''
        Get the number of riders.
        '''
        return len(self.riders)


    def press_up_button(self):
        """
        Simulate a user pressing the UP button.
        """