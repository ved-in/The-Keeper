import pygame
import constants
import core.day_cycle as day_cycle
import core.view as view


def draw(screen):
    # show the current day number and the time-of-day progress bar
    _draw_label(screen, f"day {day_cycle.day}", (200, 195, 215), 16, 16)
    _draw_progress(screen)


def draw_night(screen):
    # during night scenes only show the night number, no progress bar
    _draw_label(screen, f"night {day_cycle.day}", (120, 110, 150), 20, 20)


def _draw_label(screen, text, color, x_pos, y_pos):
    font = view.font(13, constants.FONT_PATH)
    screen.blit(font.render(text, True, color), view.point(x_pos, y_pos))


def _draw_progress(screen):
    # outer border rect
    border = view.rect(16, 38, 132, 10)
    radius = max(1, view.scale(4))
    # inner rect is slightly smaller to leave a visible border gap
    inner = border.inflate(-view.scale(2), -view.scale(2))

    # draw the three layers: dark background, border stroke, inner track
    pygame.draw.rect(screen, (28, 26, 38), border, border_radius=radius)
    pygame.draw.rect(screen, (82, 76, 94), border, width=max(1, view.scale(1)), border_radius=radius)
    pygame.draw.rect(screen, (66, 74, 100), inner, border_radius=radius)

    # fill portion grows from left to right as the day progresses
    fill = inner.copy()
    fill.width = int(inner.width * day_cycle.progress())
    if fill.width:
        pygame.draw.rect(screen, (180, 166, 124), fill, border_radius=radius)
