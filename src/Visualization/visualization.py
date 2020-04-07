"""
Author: Owen Barbour
"""

import pyglet as pyglet
import time
from pyglet import gl
from src.building import Building
from src.elevator import Elevator
from src.ElevatorState import ElevatorState


class Visualization:
    """
    Graphics/visualization class.
    """
    pyglet_window = pyglet.window.Window(height=700, width=675, caption='Simulation', resizable=False)  # width=1200
    color_pairs = (120, 0, 0, 100) * int(8 / 2)
    color_elevator_shaft_even = (0, 115, 230, 50) * 4
    color_elevator_even = (0, 115, 230, 100) * 4
    color_elevator_even_2 = (0, 115, 230, 20) * 4
    color_elevator_shaft_odd = (255, 102, 0, 50) * 4
    color_elevator_odd = (255, 102, 0, 100) * 4
    color_elevator_odd_2 = (255, 102, 0, 20) * 4
    background_color = (.95, .95, .95, 1)

    color_green = (62, 148, 72)  # 0, 230, 0
    color_red = (148, 62, 76)  # 255, 51, 0
    color_yellow = (148, 148, 62)  # 255, 255, 0
    color_gray = (128, 128, 128)

    def __init__(self, building):
        """
        Creates the pyglet visualization components for seeing elevator movements
        """
        # Property init
        self.building = building
        self.n_floors = building.n_floors
        self.n_elevators = len(building.elevators)

        # Component coordinate locations
        """
        self.pos_elevators = []
        self.pos_elevator_shafts = []
        self.elev_section_min_x = 750
        self.elev_section_min_y = 50
        self.elev_section_max_x = 1150
        self.elev_section_max_y = 650
        self.dist_bt_elev_ratio = .8
        self.floor_section_min_x = 575
        self.floor_section_max_x = 725
        """
        self.pos_elevators = []
        self.pos_elevator_shafts = []
        self.elev_section_min_x = 225
        self.elev_section_min_y = 50
        self.elev_section_max_x = 625
        self.elev_section_max_y = 650
        self.dist_bt_elev_ratio = .8
        self.floor_section_min_x = 50
        self.floor_section_max_x = 200

        # Determine elevator/shaft coordinates based on above parameters
        self.elevator_component_positions()

        # Pyglet shader and function init
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glClearColor(*self.background_color)
        self.on_draw = self.pyglet_window.event(self.on_draw)
        self.on_resize = self.pyglet_window.event(self.on_resize)
        self.on_key_press = self.pyglet_window.event(self.on_key_press)
        self.on_close = self.pyglet_window.event(self.on_close)
        self.alive = 1

        '''
        self.label = pyglet.text.Label('Hello, world', font_name='Times New Roman', font_size=36,
                                       x=self.pyglet_window.width // 2, y=self.pyglet_window.height // 2,
                                       anchor_x='center', anchor_y='center')
        self.quad = pyglet.graphics.vertex_list(4, ('v2i', (10, 10,  100, 10, 100, 100, 10, 100)),
                                                ('c3B', (0, 0, 255, 0, 0, 255, 0, 255, 0,  0, 255, 0)))
        self.quad2 = pyglet.graphics.vertex_list(4, ('v2f', (100, 100, 300, 100, 300, 300, 100, 300)),
                                                 ('c4B', self.color_pairs))
        '''

    # @pyglet_window.event
    def on_draw(self):
        # print("Running on_draw")
        self.pyglet_window.clear()

        # self.label.draw()
        # self.quad.draw(pyglet.gl.GL_QUADS)
        # self.quad2.draw(pyglet.gl.GL_QUADS)
        elevator_floors_batch = self.draw_elevator_floors()
        elevator_shafts_batch = self.draw_elevator_shafts()
        elevators_batch = self.draw_elevators()
        floor_batch = self.draw_floor_information()
        elevator_floors_batch.draw()
        elevator_shafts_batch.draw()
        elevators_batch.draw()
        floor_batch.draw()

        self.pyglet_window.flip()

    # Default implementation (not used; resizing currently turned off)
    def on_resize(self, width, height):
        pyglet.gl.glViewport(0, 0, width, height)
        pyglet.gl.glMatrixMode(gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glOrtho(0, width, 0, height, -1, 1)
        pyglet.gl.glMatrixMode(gl.GL_MODELVIEW)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:  # [ESC]
            self.alive = 0

    def on_close(self):
        self.alive = 0

    @staticmethod
    def create_quad_vertex_list(x, y, width, height):
        return x, y, x + width, y, x + width, y + height, x, y + height

    def elevator_component_positions(self):
        min_x = self.elev_section_min_x
        min_y = self.elev_section_min_y
        max_x = self.elev_section_max_x
        max_y = self.elev_section_max_y

        x_range = max_x - min_x
        x_elev_width = x_range / (self.n_elevators + ((self.n_elevators - 1) * self.dist_bt_elev_ratio))
        if self.n_elevators > 1:
            x_elev_dist_bt = (x_range - (x_elev_width * self.n_elevators)) / (self.n_elevators - 1)
        else:
            x_elev_dist_bt = 0

        y_range = max_y - min_y
        y_floor_dist = y_range / self.n_floors

        shaft_height_meters = self.n_floors * self.building.floor_dist
        elev_height_px = y_range / shaft_height_meters * self.building.elev_height

        for i in range(0, self.n_elevators):
            min_elev_x = min_x + i * (x_elev_width + x_elev_dist_bt)
            max_elev_x = min_x + (i + 1) * x_elev_width + i * x_elev_dist_bt
            self.pos_elevator_shafts.append((min_elev_x, min_y, max_elev_x, max_y))
            self.pos_elevators.append((min_elev_x, min_y, max_elev_x, min_y + elev_height_px))

    def draw_elevator_floors(self):
        batch = pyglet.graphics.Batch()
        y_range = self.elev_section_max_y - self.elev_section_min_y
        y_floor_dist = y_range / self.n_floors
        for i in range(0, self.n_floors):
            floor_y = self.elev_section_min_y + i * y_floor_dist
            # self.canvas.create_line(min_x, floor_y, max_x, floor_y)
            batch.add(2, pyglet.gl.GL_LINES, None, ('v2f', (self.elev_section_min_x, floor_y, self.elev_section_max_x,
                                                            floor_y)), ('c3B', (0, 0, 0, 0, 0, 0)))
        return batch

    def draw_elevator_shafts(self):
        batch = pyglet.graphics.Batch()
        for i in range(0, len(self.pos_elevator_shafts)):
            min_elev_x = self.pos_elevator_shafts[i][0]
            min_y = self.pos_elevator_shafts[i][1]
            max_elev_x = self.pos_elevator_shafts[i][2]
            max_y = self.pos_elevator_shafts[i][3]
            if i % 2 == 0:
                # self.canvas.create_rectangle(min_elev_x, min_y, max_elev_x, max_y, fill="#ffd4d4")
                batch.add(4, pyglet.gl.GL_QUADS, None,
                          ('v2f', (min_elev_x, min_y, max_elev_x, min_y, max_elev_x, max_y, min_elev_x, max_y)),
                          ('c4B', self.color_elevator_shaft_even))
            else:
                # self.canvas.create_rectangle(min_elev_x, min_y, max_elev_x, max_y, fill="#d4e5ff")
                batch.add(4, pyglet.gl.GL_QUADS, None,
                          ('v2f', (min_elev_x, min_y, max_elev_x, min_y, max_elev_x, max_y, min_elev_x, max_y)),
                          ('c4B', self.color_elevator_shaft_odd))
        return batch

    def draw_elevators(self):
        batch = pyglet.graphics.Batch()
        border_size = 3

        for i in range(0, len(self.pos_elevators)):
            y_range = self.elev_section_max_y - self.elev_section_min_y
            shaft_height_meters = self.n_floors * self.building.floor_dist
            elev_y_offset_px = y_range / shaft_height_meters * self.building.elevators[i].position

            elev_min_x = self.pos_elevators[i][0]
            elev_min_y = self.pos_elevators[i][1] + elev_y_offset_px
            elev_max_x = self.pos_elevators[i][2]
            elev_max_y = self.pos_elevators[i][3] + elev_y_offset_px
            if i % 2 == 0:
                batch.add(4, pyglet.gl.GL_QUADS, None,
                          ('v2f', (elev_min_x, elev_min_y, elev_max_x, elev_min_y, elev_max_x, elev_max_y, elev_min_x,
                                   elev_max_y)), ('c4B', self.color_elevator_even))
                '''batch.add(4, pyglet.gl.GL_QUADS, None,
                          ('v2f', (min_x+border_size, min_y+border_size, max_x-border_size, min_y+border_size, 
                          max_x-border_size, max_y-border_size, min_x+border_size, max_y-border_size)),
                          ('c4B', self.color_elevator_even_2))'''
            else:
                batch.add(4, pyglet.gl.GL_QUADS, None,
                          ('v2f', (elev_min_x, elev_min_y, elev_max_x, elev_min_y, elev_max_x, elev_max_y, elev_min_x,
                                   elev_max_y)), ('c4B', self.color_elevator_odd))
            self.draw_elevator_passengers(batch, self.building.elevators[i], elev_min_x, elev_min_y, elev_max_x,
                                          elev_max_y)
            self.draw_elevator_outline(batch, self.building.elevators[i], border_size, elev_min_x, elev_min_y,
                                       elev_max_x, elev_max_y)
        return batch

    # Displays the number of passengers in an elevator on the center of the elevator
    @staticmethod
    def draw_elevator_passengers(batch, elevator, elev_min_x, elev_min_y, elev_max_x, elev_max_y):
        pyglet.text.Label(str(len(elevator.riders)), font_name='Times New Roman', font_size=12,
                          x=((elev_min_x + elev_max_x) / 2), y=((elev_min_y + elev_max_y) / 2),
                          anchor_x='center', anchor_y='center', batch=batch)

    # Elevator outline is non-transparent green/red indicating UP and DOWN ElevatorState
    # No outline for NO_ACTION or LOADING_UNLOADING ElevatorState
    # Will have to use shaders, or draw 1-4 polygons
    def draw_elevator_outline(self, batch, elevator, border_size, elev_min_x, elev_min_y, elev_max_x, elev_max_y):
        rect_bottom = (elev_min_x, elev_min_y, elev_max_x, elev_min_y, elev_max_x, elev_min_y + border_size,
                       elev_min_x, elev_min_y + border_size)
        rect_right = (elev_max_x - border_size, elev_min_y, elev_max_x, elev_min_y, elev_max_x, elev_max_y,
                      elev_max_x - border_size, elev_max_y)
        rect_top = (elev_min_x, elev_max_y - border_size, elev_max_x, elev_max_y - border_size, elev_max_x, elev_max_y,
                    elev_min_x, elev_max_y)
        rect_left = (elev_min_x, elev_min_y, elev_min_x + border_size, elev_min_y, elev_min_x + border_size, elev_max_y,
                     elev_min_x, elev_max_y)

        if elevator.state == ElevatorState.NO_ACTION:
            self.add_rect_solid_outline(batch, rect_bottom, rect_right, rect_top, rect_left, self.color_gray * 4)
        elif elevator.state == ElevatorState.LOADING_UNLOADING:
            self.add_rect_solid_outline(batch, rect_bottom, rect_right, rect_top, rect_left, self.color_yellow * 4)
        elif elevator.state == ElevatorState.UP:
            self.add_rect_solid_outline(batch, rect_bottom, rect_right, rect_top, rect_left, self.color_green * 4)
        elif elevator.state == ElevatorState.DOWN:
            self.add_rect_solid_outline(batch, rect_bottom, rect_right, rect_top, rect_left, self.color_red * 4)

    @staticmethod
    def add_rect_solid_outline(batch, rect_bottom, rect_right, rect_top, rect_left, color_rgb):
        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f', rect_bottom), ('c3B', color_rgb))
        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f', rect_right), ('c3B', color_rgb))
        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f', rect_top), ('c3B', color_rgb))
        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f', rect_left), ('c3B', color_rgb))

    # x coordinate region defined by floor_section_min_x/floor_section_max_x and y coordinate region defined by
    # elev_section_min_y/elev_section_max_y. The placement of the text (height) is determined by the tuples in
    # pos_elevators; the y-coor will be the middle of the 2nd and 4th element of the tuple for the floor.
    def draw_floor_information(self):
        batch = pyglet.graphics.Batch()

        # Column for up button pressed, down button pressed, and number of people waiting
        x_total_range = self.floor_section_max_x - self.floor_section_min_x
        people_waiting_column_x = self.floor_section_min_x + (x_total_range / 6)
        up_button_column_x = self.floor_section_min_x + (x_total_range / 3) + (x_total_range / 6)
        down_button_column_x = self.floor_section_min_x + (x_total_range / 3) * 2 + (x_total_range / 6)

        # Up/down arrow coordinate offsets
        arrow_offset_y = 5
        arrow_offset_x = 5
        text_offset_y = 3
        label_offset_y = 35

        # For each floor, add the number each of the above described columns
        for i in range(0, self.n_floors):
            y_range = self.elev_section_max_y - self.elev_section_min_y
            y_floor_dist = y_range / self.n_floors

            min_y_floor = self.pos_elevators[0][1]
            max_y_top_of_elev = self.pos_elevators[0][3]
            middle_y = (min_y_floor + max_y_top_of_elev) / 2 + i * y_floor_dist

            pyglet.text.Label(str(len(self.building.floors[i].people_waiting)), font_name='Times New Roman',
                              font_size=12, x=people_waiting_column_x, y=middle_y + text_offset_y, anchor_x='center',
                              anchor_y='center', batch=batch, color=(0, 0, 0, 255))
            if self.building.floors[i].up_pressed:
                batch.add(3, pyglet.gl.GL_TRIANGLES, None,
                          ('v2f', (up_button_column_x - arrow_offset_x, middle_y - arrow_offset_y,
                                   up_button_column_x + arrow_offset_x, middle_y - arrow_offset_y,
                                   up_button_column_x, middle_y + arrow_offset_y)), ('c3B', self.color_green * 3))
            if self.building.floors[i].down_pressed:
                batch.add(3, pyglet.gl.GL_TRIANGLES, None,
                          ('v2f', (down_button_column_x + arrow_offset_x, middle_y + arrow_offset_y,
                                   down_button_column_x - arrow_offset_x, middle_y + arrow_offset_y,
                                   down_button_column_x, middle_y - arrow_offset_y)), ('c3B', self.color_red * 3))

            # Add labels for the columns - WAITING, UP, DOWN
            if i == self.n_floors - 1:
                pyglet.text.Label("WAITING", font_name='Times New Roman', font_size=12, x=people_waiting_column_x,
                                  y=middle_y + text_offset_y + label_offset_y, anchor_x='center', anchor_y='center',
                                  batch=batch, color=(0, 0, 0, 255))
                pyglet.text.Label("UP", font_name='Times New Roman', font_size=12, x=up_button_column_x,
                                  y=middle_y + text_offset_y + label_offset_y, anchor_x='center', anchor_y='center',
                                  batch=batch, color=(0, 0, 0, 255))
                pyglet.text.Label("DOWN", font_name='Times New Roman', font_size=12, x=down_button_column_x,
                                  y=middle_y + text_offset_y + label_offset_y, anchor_x='center', anchor_y='center',
                                  batch=batch, color=(0, 0, 0, 255))

        return batch


def visualization_test_main():
    elevators = [Elevator(1), Elevator(2), Elevator(3), Elevator(4)]
    building = Building(name=1, elevators=elevators, n_floors=10)
    vis = Visualization(building)

    # Option 1: pyglet.app.run()
    # Option 2: event_loop = pyglet.app.EventLoop()
    # event_loop.run()
    # Option 3: custom event loop which dispatches an on_draw event, which updates the screen to the current state
    vis.pyglet_window.dispatch_event("on_draw")
    while vis.alive == 1:
        print("Running loop")
        time.sleep(7)

        # These three lines are needed
        pyglet.clock.tick()
        vis.pyglet_window.dispatch_events()
        vis.pyglet_window.dispatch_event("on_draw")

        building.elevators[0].position += 3
        building.elevators[2].position += 2
        building.elevators[0].state = ElevatorState.LOADING_UNLOADING
        building.elevators[1].state = ElevatorState.UP
        building.elevators[2].state = ElevatorState.DOWN
        building.elevators[3].state = ElevatorState.NO_ACTION
        # vis.pyglet_window.flip()


if __name__ == "__main__":
    visualization_test_main()
