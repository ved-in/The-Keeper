import pygame
import core.game as game
import core.view as view

pygame.init()
pygame.font.init()

WINDOW_W = 1280
WINDOW_H = 720
MODE_ORDER = ["windowed", "borderless", "fullscreen"]
mode_index = 0

pygame.display.set_caption("The Keeper")
clock = pygame.time.Clock()

game.init()


def set_mode(name):
    desktop_size = pygame.display.get_desktop_sizes()[0]

    if name == "windowed":
        screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    elif name == "borderless":
        screen = pygame.display.set_mode(desktop_size, pygame.NOFRAME)
    else:
        screen = pygame.display.set_mode(desktop_size, pygame.FULLSCREEN)

    view.set_size(screen.get_size())
    return screen


screen = set_mode(MODE_ORDER[mode_index])


running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            mode_index = (mode_index + 1) % len(MODE_ORDER)
            screen = set_mode(MODE_ORDER[mode_index])
            continue
        if event.type == pygame.WINDOWSIZECHANGED:
            view.set_size((event.x, event.y))
        game.handle_event(event)

    game.update(dt)
    game.draw(screen)
    pygame.display.flip()

pygame.quit()
