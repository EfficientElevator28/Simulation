"""
Author: Owen Barbour
"""

import pyglet as pyglet
from pyglet import gl
from src.building import Building
from src.elevator import Elevator


class Visualization:
    """
    Graphics/visualization class.
    """
    pyglet_window = pyglet.window.Window(height=700, width=1200, caption='Simulation', resizable=False)
    color_pairs = (120, 0, 0, 100) * int(8 / 2)
    color_elevator_shaft_even = (0, 115, 230, 50) * 4
    color_elevator_even = (0, 115, 230, 100) * 4
    color_elevator_even_2 = (0, 115, 230, 20) * 4
    color_elevator_shaft_odd = (255, 102, 0, 50) * 4
    color_elevator_odd = (255, 102, 0, 100) * 4
    color_elevator_odd_2 = (255, 102, 0, 20) * 4
    background_color = (.95, .95, .95, 1)

    def __init__(self, building):
        """
        Creates the pyglet visualization components for seeing elevator movements
        """
        # Property init
        self.building = building
        self.n_floors = building.n_floors
        self.n_elevators = len(building.elevators)

        # Pyglet shader and function init
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glClearColor(*self.background_color)
        self.on_draw = self.pyglet_window.event(self.on_draw)
        self.on_resize = self.pyglet_window.event(self.on_resize)

        # Component coordinate locations
        self.pos_elevators = []
        self.pos_elevator_shafts = []

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
        self.pyglet_window.clear()

        # self.label.draw()
        # self.quad.draw(pyglet.gl.GL_QUADS)
        # self.quad2.draw(pyglet.gl.GL_QUADS)
        self.elevator_component_positions(750, 50, 1150, 650, .8)
        elevator_floors_batch = self.draw_elevator_floors(750, 50, 1150, 650)
        elevator_shafts_batch = self.draw_elevator_shafts()
        elevators_batch = self.draw_elevators()
        elevator_floors_batch.draw()
        elevator_shafts_batch.draw()
        elevators_batch.draw()

    # Default implementation (not used; resizing currently turned off)
    def on_resize(self, width, height):
        pyglet.gl.glViewport(0, 0, width, height)
        pyglet.gl.glMatrixMode(gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glOrtho(0, width, 0, height, -1, 1)
        pyglet.gl.glMatrixMode(gl.GL_MODELVIEW)

    @staticmethod
    def create_quad_vertex_list(x, y, width, height):
        return x, y, x + width, y, x + width, y + height, x, y + height

    def elevator_component_positions(self, min_x, min_y, max_x, max_y, dist_bt_elev_ratio):
        x_range = max_x - min_x
        x_elev_width = x_range / (self.n_elevators + ((self.n_elevators - 1) * dist_bt_elev_ratio))
        x_elev_dist_bt = (x_range - (x_elev_width * self.n_elevators)) / (self.n_elevators - 1)

        y_range = max_y - min_y
        y_floor_dist = y_range / self.n_floors

        shaft_height_meters = self.n_floors * self.building.floor_dist
        elev_height_px = y_range / shaft_height_meters * self.building.elev_height

        for i in range(0, self.n_elevators):
            min_elev_x = min_x + i * (x_elev_width + x_elev_dist_bt)
            max_elev_x = min_x + (i + 1) * x_elev_width + i * x_elev_dist_bt
            self.pos_elevator_shafts.append((min_elev_x, min_y, max_elev_x, max_y))
            self.pos_elevators.append((min_elev_x, min_y, max_elev_x, min_y + elev_height_px))

    def draw_elevator_floors(self, min_x, min_y, max_x, max_y):
        batch = pyglet.graphics.Batch()
        y_range = max_y - min_y
        y_floor_dist = y_range / self.n_floors
        for i in range(0, self.n_floors):
            floor_y = min_y + i * y_floor_dist
            # self.canvas.create_line(min_x, floor_y, max_x, floor_y)
            batch.add(2, pyglet.gl.GL_LINES, None, ('v2f', (min_x, floor_y, max_x, floor_y)),
                      ('c3B', (0, 0, 0, 0, 0, 0)))
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
        border_size = 2
        for i in range(0, len(self.pos_elevators)):
            min_x = self.pos_elevators[i][0]
            min_y = self.pos_elevators[i][1]
            max_x = self.pos_elevators[i][2]
            max_y = self.pos_elevators[i][3]
            if i % 2 == 0:
                batch.add(4, pyglet.gl.GL_QUADS, None,
                          ('v2f', (min_x, min_y, max_x, min_y, max_x, max_y, min_x, max_y)),
                          ('c4B', self.color_elevator_even))
                '''batch.add(4, pyglet.gl.GL_QUADS, None,
                          ('v2f', (min_x+border_size, min_y+border_size, max_x-border_size, min_y+border_size, 
                          max_x-border_size, max_y-border_size, min_x+border_size, max_y-border_size)),
                          ('c4B', self.color_elevator_even_2))'''
            else:
                batch.add(4, pyglet.gl.GL_QUADS, None,
                          ('v2f', (min_x, min_y, max_x, min_y, max_x, max_y, min_x, max_y)),
                          ('c4B', self.color_elevator_odd))
        return batch

    # Displays the number of passengers in an elevator on the center of the elevator
    def draw_elevator_passengers(self):
        pass

    # Elevator outline is non-transparent green/red indicating UP and DOWN ElevatorState
    # No outline for NO_ACTION or LOADING_UNLOADING ElevatorState
    def draw_elevator_outline(self):
        pass


def main():
    elevators = [Elevator(1), Elevator(2), Elevator(3), Elevator(4)]
    building = Building(name=1, elevators=elevators, n_floors=10)
    vis = Visualization(building)
    pyglet.app.run()


if __name__ == "__main__":
    main()
