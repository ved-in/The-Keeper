import pygame
import core.day_cycle as day_cycle
import ui.dialogue as dialogue
import core.player as player
import scenes.lighthouse as lighthouse
import constants

done = False
_player = player.make_player()


def init():
    global done, _player
    done = False
    _player = player.make_player()

def handle_event(event):
    global done
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if not dialogue.advance():
                done = True  # no more lines, night is over

def update(dt):
    global _player
    if not dialogue.active():
        player.update(_player, dt)

def draw(screen):
    screen.fill((25, 20, 45))
    
    lighthouse.draw(screen)
    
    # beacon
    pygame.draw.circle(screen, (255, 230, 120), (480 + player.ELEMENTS_OFFSET, 200), 40)
    # making it pulse would be nice
    
    # puts current night number on the top left of screen
    font = pygame.font.SysFont("monospace", 13)
    label = font.render(f"night {day_cycle.day}", True, (120, 110, 150))
    screen.blit(label, (20, 20))
    
    # load dialogues, later replace by tasks + dialogues ;)
    if not dialogue.active() and not done:
        script = constants.SCRIPTS.get(day_cycle.day, ["The dark holds its breath."])
        dialogue.show(script)
    
    # draws player and dialogues on the screen
    player.draw(screen, _player)
    dialogue.draw(screen)
    