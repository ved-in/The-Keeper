import pygame
import core.game as game
import core.view as view

import core.sound as sound

# window size when running in windowed mode
WINDOW_W = 1280
WINDOW_H = 720

# the three display modes we can cycle through with F11
MODE_ORDER = ["windowed", "borderless", "fullscreen"]


def set_mode(name):
    # get the actual monitor resolution so borderless and fullscreen fill it exactly
    desktop_size = pygame.display.get_desktop_sizes()[0]

    if name == "windowed":
        screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    elif name == "borderless":
        # borderless fills the screen but skips the OS fullscreen transition
        screen = pygame.display.set_mode(desktop_size, pygame.NOFRAME)
    else:
        screen = pygame.display.set_mode(desktop_size, pygame.FULLSCREEN)

    # tell the view module how big the window is so it can scale everything correctly
    view.set_size(screen.get_size())
    game.handle_resize()
    return screen


def run_frame(clock, screen, mode_index):
    # dt is the time in seconds since the last frame, used to make movement speed consistent
    dt = clock.tick(60) / 1000.0
    running = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, screen, mode_index

        # F11 cycles through windowed, borderless, fullscreen
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            mode_index = (mode_index + 1) % len(MODE_ORDER)
            screen = set_mode(MODE_ORDER[mode_index])
            continue

        # play UI sound on any key that isn't movement / F11 - annoying so no >:(
        _MOVEMENT_KEYS = {
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
            pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s,
            pygame.K_F11,
            pygame.K_F9,
        }
        if event.type == pygame.KEYDOWN and event.key not in _MOVEMENT_KEYS:
            sound.play_button()

        # if the user resizes the window manually, update the view scaling
        if event.type == pygame.WINDOWSIZECHANGED:
            view.set_size((event.x, event.y))
            game.handle_resize()
        game.handle_event(event)

    game.update(dt)
    game.draw(screen)
    pygame.display.flip()
    return running, screen, mode_index


def main():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.display.set_caption("The Keeper")

    clock = pygame.time.Clock()
    mode_index = 0

    # display must be created before game.init() because loading assets needs a surface
    screen = set_mode(MODE_ORDER[mode_index])
    game.init()

    running = True
    while running:
        running, screen, mode_index = run_frame(clock, screen, mode_index)

    pygame.quit()


if __name__ == "__main__":
    main()
