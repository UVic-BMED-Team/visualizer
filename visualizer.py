import math
import pyglet
from pyglet.gl import GL_QUADS, GL_POINTS

WINDOW_HEIGHT = 600 # pixel height of viewer window
WINDOW_WIDTH = int((2 / 3) * WINDOW_HEIGHT) # pixel width of viewer window
CIRCLE_VERTS = 1440 # number of vertices used to draw top view circle
TOPX = int(WINDOW_WIDTH / 2) # x coord of center of top view
TOPY = int((7 / 9) * WINDOW_HEIGHT) # y coord of center of top view
BOTTOMX = int(WINDOW_WIDTH / 2) # x coord of center of side view
BOTTOMY = int(WINDOW_HEIGHT / 3) # y coord of center of side view
RADIUS = int(WINDOW_WIDTH / 4) # radius of both views
HEIGHT = int((4 / 9) * WINDOW_HEIGHT) # height in pixels of side on view
MAXANGLE = 270 # maximum angle the probe/emitter can rotate
DC_LENGTH = int((0.5 / 9) * WINDOW_HEIGHT) # side length of DACI emitter
US_LENGTH = int((0.5 / 9) * WINDOW_HEIGHT) # side length of ultrasound probe
DC_COLOUR = (255, 255, 255) # RGB colour code for DACI emitter
US_COLOUR = (255, 0, 0) # RGB colour code for ultrasound probe
FONTSIZE = int(WINDOW_HEIGHT / 64)
LOC = (0.5 / 9) * WINDOW_HEIGHT

def angle_to_xy(angle, cx, cy, r):
    rads = math.radians(angle)
    x = cx + (math.cos(rads) * r)
    y = cy + (math.sin(rads) * r)
    return x, y

def circle(max_verts, center_x, center_y, radius, batch=None):
    """
    Draw a white circle outline using max_verts points centered at
    (center_x, center_y) with a radius of radius pixels.
    """
    if batch is None: batch = pyglet.graphics.Batch()
    angle = 360 / max_verts
    for i in range(max_verts):
        x, y = angle_to_xy(angle * i, center_x, center_y, radius)
        batch.add(1, GL_POINTS, None, ('v2f', (x, y)))
    return batch

def square(x, y, r, colour, batch=None):
    """
    Draw a filled in square centered at (x, y) with length/height of r pixels.
    """
    R, G, B = colour[0], colour[1], colour[2]
    if batch is None: batch = pyglet.graphics.Batch()
    tp = y + (r / 2)
    bm = y - (r / 2)
    rt = x + (r / 2)
    lf = x - (r / 2)
    batch.add(4, GL_QUADS, None, ('v2f', (lf, bm, lf, tp, rt, tp, rt, bm)),
                                 ('c3B', (R, G, B, R, G, B, R, G, B, R, G, B)))
    return batch

def rectangle(x, y, w, h, batch=None):
    """
    Draw a white rectangular outline centered at (x, y) with height h pixels
    and width w pixels.
    """
    if batch is None: batch = pyglet.graphics.Batch()
    tp = y + (h / 2)
    bm = y - (h / 2)
    rt = x + (w / 2)
    lf = x - (w / 2)
    for i in range(h):
        batch.add(1, GL_POINTS, None, ('v2f', (lf, bm + i)))
        batch.add(1, GL_POINTS, None, ('v2f', (rt, bm + i)))
    for i in range(w):
        batch.add(1, GL_POINTS, None, ('v2f', (lf + i, bm)))
        batch.add(1, GL_POINTS, None, ('v2f', (lf + i, tp)))
    return batch

def redraw_top_view(angle, radius):
    """
    Redraw the daci emitter and ultrasound probe at new angle and radius on the
    top down view.
    """
    ux, uy = angle_to_xy(angle, TOPX, TOPY, radius)
    dx, dy = angle_to_xy((angle + 180) % 360, TOPX, TOPY, RADIUS)
    ultrasound = square(ux, uy, US_LENGTH, US_COLOUR)
    daci = square(dx, dy, DC_LENGTH, DC_COLOUR)
    return ultrasound, daci

def redraw_side_view(height, radius):
    """
    Redraw the daci emitter and ultrasound probe at new height adn radius on
    the side on view.
    """
    ultrasound = square(BOTTOMX + radius,
                        BOTTOMY - (HEIGHT // 2) + height,
                        US_LENGTH, US_COLOUR)
    daci = square(BOTTOMX - RADIUS,
                  BOTTOMY - (HEIGHT // 2) + height,
                  DC_LENGTH, DC_COLOUR)
    return ultrasound, daci

z = 0
r = RADIUS
h = HEIGHT
step = 0
# TODO: update this with code that gets real values from device
def get_new_values():
    """
    Produce values for demoing visualizer
    """
    global z, r, h, step

    if step == 0 or step == 5: # rotate forwards
        z += 1
        if z >= MAXANGLE:
            z = MAXANGLE - 1
            step = (step + 1) % 7
    if step == 2 or step == 7: # rotate back
        z -= 1
        if z < 0:
            z = 0
            step = (step + 1) % 7
    if step == 1: # shrink radius
        r -= 1
        if r <= (RADIUS // 2):
            r = (RADIUS // 2)
            step = (step + 1) % 7
    if step == 4: # grow radius
        r += 1
        if r >= RADIUS:
            r = RADIUS
            step = (step + 1) % 7
    if step == 3: # lower
        h -= 1
        if h < 0:
            h = 0
            step = (step + 1) % 7
    if step == 6: # raise
        h += 1
        if h >= HEIGHT:
            h = HEIGHT
            step = (step + 1) % 7
    return z, r, h


window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

bg = pyglet.graphics.Batch() # batch of graphics that make up the background
bg = circle(CIRCLE_VERTS, TOPX, TOPY, RADIUS, batch=bg)
bg = rectangle(BOTTOMX, BOTTOMY, 2 * RADIUS, HEIGHT, batch=bg)
bg = square(LOC // 2, LOC, US_LENGTH // 2, US_COLOUR, batch=bg)
bg = square(LOC // 2, LOC // 2, DC_LENGTH // 2, DC_COLOUR, batch=bg)

us_label = pyglet.text.Label('Ultrasound Probe', font_size=FONTSIZE,
                             x=LOC, y=LOC, batch=bg)
dc_label = pyglet.text.Label('DACI Emitter', font_size=FONTSIZE, x=LOC,
                             y=LOC // 2,
                             batch=bg)
top_label = pyglet.text.Label('Top View:', font_size=FONTSIZE, x=5,
                              y=WINDOW_HEIGHT - (LOC // 2), batch=bg)
bottom_label = pyglet.text.Label('Side View:', font_size=FONTSIZE, x=5,
                                 y=(WINDOW_HEIGHT // 2) + LOC, batch=bg)


def update(dt):
    window.clear()
    bg.draw()

    angle, radius, height = get_new_values()

    top_us, top_daci = redraw_top_view(angle, radius)
    top_us.draw()
    top_daci.draw()

    bottom_us, bottom_daci = redraw_side_view(height, radius)
    bottom_us.draw()
    bottom_daci.draw()

pyglet.clock.schedule_interval(update, 1 / 120)
pyglet.app.run()
