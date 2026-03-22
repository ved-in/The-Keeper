import pygame
import core.player as player
import constants
import core.view as view

def draw(screen):
    pygame.draw.rect(screen, (55, 50, 70), view.rect(0 + player.ELEMENTS_OFFSET, constants.GROUND_Y, view.BASE_W, 140))        # ground
    pygame.draw.rect(screen, (200, 195, 185), view.rect(430 + player.ELEMENTS_OFFSET, 120, 100, constants.GROUND_Y - 120))  # tower
    pygame.draw.rect(screen, (240, 220, 130), view.rect(420 + player.ELEMENTS_OFFSET, 100, 120, 40))              # lantern
