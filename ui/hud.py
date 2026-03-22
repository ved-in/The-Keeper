import pygame
import core.day_cycle as day_cycle
import core.view as view

FONT_PATH = "assets/fonts/IMFellEnglish-Regular.ttf"

def draw(screen):
    frame = view.content_rect()
    font = view.font(13, FONT_PATH)
    
    # day_cycle.day is a variable of current day number and we just blit it onto the screen
    screen.blit(font.render(f"day {day_cycle.day}", True, (200, 195, 215)), (frame.x + view.scale(16), frame.y + view.scale(16)))

    # insert time bar here <-
    # we will get current progress through day_cycle.progress function and make a bar for it
