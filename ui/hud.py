import pygame
import core.day_cycle as day_cycle


def draw(screen):
    font = pygame.font.SysFont("monospace", 13)
    
    # day_cycle.day is a variable of current day number and we just blit it onto the screen
    screen.blit(font.render(f"day {day_cycle.day}", True, (200, 195, 215)), (16, 16))

    # insert time bar here <-
    # we will get current progress through day_cycle.progress function and make a bar for it
