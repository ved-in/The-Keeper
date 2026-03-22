import pygame
import core.game as game

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((960, 540))
pygame.display.set_caption("The Keeper")
clock = pygame.time.Clock()

game.init()

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_event(event)

    game.update(dt)
    game.draw(screen)
    pygame.display.flip()

pygame.quit()
