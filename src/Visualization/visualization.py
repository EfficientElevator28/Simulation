"""
Author: Owen Barbour
"""

import pyglet as pyglet
from pyglet import window
from pyglet import gl


class Visualization:
    """
    Graphics/visualization class.
    """
    pyglet_window = pyglet.window.Window(height=700, width=1200, caption='Simulation', resizable=True)
    color_pairs = (120, 0, 0, 100) * int(8 / 2)
    color_elevator_shaft_even = (0, 115, 230, 100) * 4
    color_elevator_shaft_odd = (255, 102, 0, 100) * 4
    background_color = (.95, .95, .95, 1)

    def __init__(self, n_floors, n_elevators):
        """
        Creates the pyglet visualization components for seeing elevator movements
        """
        self.n_floors = n_floors
        self.n_elevators = n_elevators

        # self.pyglet_window = pyglet.window.Window()
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.label = pyglet.text.Label('Hello, world', font_name='Times New Roman', font_size=36,
                                       x=self.pyglet_window.width // 2, y=self.pyglet_window.height // 2,
                                       anchor_x='center', anchor_y='center')
        self.quad = pyglet.graphics.vertex_list(4, ('v2i', (10, 10,  100, 10, 100, 100, 10, 100)),
                                                ('c3B', (0, 0, 255, 0, 0, 255, 0, 255, 0,  0, 255, 0)))
        self.quad2 = pyglet.graphics.vertex_list(4, ('v2f', (100, 100, 300, 100, 300, 300, 100, 300)),
                                                 ('c4B', self.color_pairs))

        gl.glClearColor(*self.background_color)
        # self.rect = pyglet.graphics.draw

        self.on_draw = self.pyglet_window.event(self.on_draw)
        self.on_resize = self.pyglet_window.event(self.on_resize)

    # @pyglet_window.event
    def on_draw(self):
        self.pyglet_window.clear()

        self.label.draw()
        # self.quad.draw(pyglet.gl.GL_QUADS)
        # self.quad2.draw(pyglet.gl.GL_QUADS)
        elevator_floors_batch = self.draw_elevator_floors(600, 50, 1150, 650)
        elevator_shafts_batch = self.draw_elevator_shafts(600, 50, 1150, 650, .8)
        elevator_floors_batch.draw()
        elevator_shafts_batch.draw()

    # Doesn't currently do anything different
    def on_resize(self, width, height):
        pyglet.gl.glViewport(0, 0, width, height)
        pyglet.gl.glMatrixMode(gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glOrtho(0, width, 0, height, -1, 1)
        pyglet.gl.glMatrixMode(gl.GL_MODELVIEW)

    @staticmethod
    def create_quad_vertex_list(x, y, width, height):
        return x, y, x + width, y, x + width, y + height, x, y + height

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

    def draw_elevator_shafts(self, min_x, min_y, max_x, max_y, dist_bt_elev_ratio):
        batch = pyglet.graphics.Batch()
        x_range = max_x - min_x
        x_elev_width = x_range / (self.n_elevators + ((self.n_elevators - 1) * dist_bt_elev_ratio))
        x_elev_dist_bt = (x_range - (x_elev_width * self.n_elevators)) / (self.n_elevators - 1)
        for i in range(0, self.n_elevators):
            min_elev_x = min_x + i * (x_elev_width + x_elev_dist_bt)
            max_elev_x = min_x + (i + 1) * x_elev_width + i * x_elev_dist_bt
            # self.create_rectangle_opacity(min_elev_x, min_y, max_elev_x, max_y, fill="#ff3636", alpha=.8)  # #ff3636
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


def main():
    vis = Visualization(12, 4)
    pyglet.app.run()


if __name__ == "__main__":
    main()
