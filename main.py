import pygame
import core.game as game
import core.view as view

WINDOW_W = 1280
WINDOW_H = 720
MODE_ORDER = ["windowed", "borderless", "fullscreen"]


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


def run_frame(clock, screen, mode_index):
    dt = clock.tick(60) / 1000.0
    running = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, screen, mode_index
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
    return running, screen, mode_index


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("The Keeper")

    clock = pygame.time.Clock()
    mode_index = 0

    game.init()
    screen = set_mode(MODE_ORDER[mode_index])

    running = True
    while running:
        running, screen, mode_index = run_frame(clock, screen, mode_index)

    pygame.quit()


if __name__ == "__main__":
    main()
