import pygame

# the resolution the game is designed for
# everything is authored at this size and then scaled to the actual window
BASE_W = 1000
BASE_H = 540

_scale = 1.0
_off_x = 0
_off_y = 0
_view_w = BASE_W
_view_h = BASE_H


def set_size(size):
    global _scale, _off_x, _off_y, _view_w, _view_h
    _view_w = max(1, int(size[0]))
    _view_h = max(1, int(size[1]))

    # pick the largest scale that fits the base resolution inside the window without stretching
    _scale = min(_view_w / BASE_W, _view_h / BASE_H)

    # center the content inside the window
    content_w = int(round(BASE_W * _scale))
    content_h = int(round(BASE_H * _scale))
    _off_x = (_view_w - content_w) // 2
    _off_y = (_view_h - content_h) // 2


def scale(value):
    # converts a size value from base resolution units to actual screen pixels
    return max(1, int(round(value * _scale)))


def x(value):
    # converts a base resolution x coordinate to a screen pixel x coordinate
    return _off_x + int(round(value * _scale))


def y(value):
    # converts a base resolution y coordinate to a screen pixel y coordinate
    return _off_y + int(round(value * _scale))


def rect(x_pos, y_pos, width, height):
    # returns a pygame.Rect scaled and offset to match the actual window size
    return pygame.Rect(x(x_pos), y(y_pos), scale(width), scale(height))


def point(x_pos, y_pos):
    # returns a screen pixel coordinate tuple from base resolution coordinates
    return (x(x_pos), y(y_pos))


def content_rect():
    # returns the rectangle representing the playable area inside the window
    return pygame.Rect(_off_x, _off_y, scale(BASE_W), scale(BASE_H))


def font(size, path=None):
    # loads a font at the correct pixel size for the current window scale
    px = scale(size)
    if path:
        try:
            return pygame.font.Font(path, px)
        except (FileNotFoundError, pygame.error):
            pass
    # fall back to the system monospace font if the custom font file is missing
    return pygame.font.SysFont("monospace", px)
