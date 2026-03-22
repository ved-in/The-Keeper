import pygame
import core.player as player
import constants

def draw(screen):
    pygame.draw.rect(screen, (55, 50, 70), pygame.Rect(0 + player.ELEMENTS_OFFSET, constants.GROUND_Y, 960, 140))        # ground
    pygame.draw.rect(screen, (200, 195, 185), pygame.Rect(430 + player.ELEMENTS_OFFSET, 120, 100, constants.GROUND_Y - 120))  # tower
    pygame.draw.rect(screen, (240, 220, 130), pygame.Rect(420 + player.ELEMENTS_OFFSET, 100, 120, 40))              # lantern