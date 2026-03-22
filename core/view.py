import pygame

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
    _scale = min(_view_w / BASE_W, _view_h / BASE_H)
    content_w = int(round(BASE_W * _scale))
    content_h = int(round(BASE_H * _scale))
    _off_x = (_view_w - content_w) // 2
    _off_y = (_view_h - content_h) // 2


def scale(value):
    return max(1, int(round(value * _scale)))


def x(value):
    return _off_x + int(round(value * _scale))


def y(value):
    return _off_y + int(round(value * _scale))


def rect(x_pos, y_pos, width, height):
    return pygame.Rect(x(x_pos), y(y_pos), scale(width), scale(height))


def point(x_pos, y_pos):
    return (x(x_pos), y(y_pos))


def content_rect():
    return pygame.Rect(_off_x, _off_y, scale(BASE_W), scale(BASE_H))


def font(size, path=None):
    px = scale(size)
    if path:
        try:
            return pygame.font.Font(path, px)
        except (FileNotFoundError, pygame.error):
            pass
    return pygame.font.SysFont("monospace", px)
