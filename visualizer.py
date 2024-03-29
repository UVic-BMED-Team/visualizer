import numpy as np
import math
import pyglet
from pyglet.gl import GL_QUADS, GL_POINTS
import skimage

WINDOW_HEIGHT = 600 # pixel height of viewer window
WINDOW_WIDTH = WINDOW_HEIGHT # pixel width of viewer window
CIRCLE_VERTS = 1440 # number of vertices used to draw top view circle
MAXANGLE = 270 # maximum angle the probe/emitter can rotate
DC_COLOUR = (255, 255, 255) # RGB colour code for DACI emitter
US_COLOUR = (255, 0, 0) # RGB colour code for ultrasound probe
TOPX = 0 # x coord of center of top view
TOPY = 0 # y coord of center of top view
BOTTOMX = 0 # x coord of center of side view
BOTTOMY = 0 # y coord of center of side view
RADIUS = 0 # radius of both views
HEIGHT = 0 # height in pixels of side on view
DC_LENGTH = 0 # side length of DACI emitter
US_LENGTH = 0 # side length of ultrasound probe
FONTSIZE = 0 # Legend/label font
LOC = 0 # general purpose value to help locate things
IMAGEX = 0 # x location of ultrasound image
IMAGEY = 0 # y location of ultrasound image
IMAGESHAPE = 0 # square side length of ultrasound image in pixels
US_IMAGE_HEIGHT = 32
US_IMAGE_WIDTH = 32

def update_values(window_width, window_height):
    """
    Given new window width and height update the size/location of the probe,
    emitter, side view, top view, and labels.
    """
    global WINDOW_HEIGHT, WINDOW_WIDTH, TOPX, TOPY, BOTTOMX, BOTTOMY, RADIUS
    global HEIGHT, DC_LENGTH, US_LENGTH, FONTSIZE, LOC, IMAGEX, IMAGEY
    global IMAGESHAPE

    WINDOW_HEIGHT = window_height
    WINDOW_WIDTH = window_width
    CIRCLE_VERTS = 1440
    TOPX = int(1.2 * (window_width / 8))
    TOPY = int((7 / 9) * window_height)
    BOTTOMX = int(1.2 * (window_width / 8))
    BOTTOMY = int(window_height / 3)
    RADIUS = int(window_width / 8)
    HEIGHT = int((4 / 9) * window_height)
    MAXANGLE = 270
    DC_LENGTH = int((0.5 / 9) * window_height)
    US_LENGTH = int((0.5 / 9) * window_height)
    FONTSIZE = int(window_height / 64)
    LOC = (0.5 / 9) * window_height
    IMAGESHAPE = int(0.99 * (0.625 * window_width))
    IMAGEX = int((0.625 * window_width) - (IMAGESHAPE / 2)) + 25
    IMAGEY = int((window_height / 2) - (IMAGESHAPE / 2))

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

update_values(WINDOW_WIDTH, WINDOW_HEIGHT)
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, resizable=True)

z = 0
r = RADIUS
h = HEIGHT
step = 0
# TODO: update this with code that gets real values from device
def get_new_values():
    """
    Produce values for demoing visualizer.
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

# TODO: overwrite this with actual data from ultrasound
# TODO: parameters are just to generate demo data, real method should just take
# a single 3d numpy array and then display it
def get_ultrasound_image(angle, max_angle, height, max_height, zoom, max_zoom):
    data = skimage.data.astronaut() # load test image
    x = int(data.shape[0] // 2 * (zoom / max_zoom))
    y = int(data.shape[1] // 2 * (zoom / max_zoom))
    data = data[x:, y:]
    data = skimage.transform.resize(data, (IMAGESHAPE, IMAGESHAPE))
    data = skimage.util.img_as_ubyte(data) # convert to 8bit unsigned int
    roll_by1 = int((angle / max_angle) * data.shape[0])
    roll_by0 = int((height / max_height) * data.shape[1])

    # everything below this is necessary to display a 3d numpy array as an RGB
    data = data[::-1] # flip image because byte conversion will also flip it
    data = np.roll(data, roll_by1, axis=1)
    data = np.roll(data, roll_by0, axis=0)
    data = data.tobytes() # convert to byte string
    im = pyglet.image.ImageData(IMAGESHAPE, IMAGESHAPE, 'RGB', data)
    im_sprite = pyglet.sprite.Sprite(im, IMAGEX, IMAGEY)
    return im_sprite

def make_background():
    """
    Return a graphic batch containing the top/side view outlines, the legend,
    and the labels.
    """
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
                                     y=(WINDOW_HEIGHT // 2) + (2 * LOC), batch=bg)
    return bg

bg = make_background()

@window.event
def on_resize(width, height):
    update_values(width, height)
    global bg
    bg = make_background()
    update(1)

@window.event
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

    ultrasound_image = get_ultrasound_image(angle, 360, height, HEIGHT,
                                            RADIUS - radius, RADIUS)
    ultrasound_image.draw()

pyglet.clock.schedule_interval(update, 1 / 120)
pyglet.app.run()
