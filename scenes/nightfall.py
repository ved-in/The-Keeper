import math
import pygame
import core.day_cycle as day_cycle
import ui.dialogue as dialogue
import core.player as player
import scenes.lighthouse as lighthouse
import constants
import core.view as view

done = False
_player = player.make_player()
_t = 0.0
FONT_PATH = "assets/fonts/IMFellEnglish-Regular.ttf"


def init():
    global done, _player, _t
    done = False
    _player = player.make_player()
    _t = 0.0

def handle_event(event):
    global done
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if not dialogue.advance():
                done = True  # no more lines, night is over

def update(dt):
    global _player, _t
    _t += dt
    dialogue.update(dt)
    if not dialogue.active():
        player.update(_player, dt)

def draw(screen):
    screen.fill(constants.SKY_COLORS["night"])
    
    lighthouse.draw(screen)
    
    # beacon
    cx = view.x(480 + player.ELEMENTS_OFFSET)
    cy = view.y(200)
    p = (math.sin(_t * 3.2) + 1.0) * 0.5
    # _t = time (increasing every frame)
    # 3.2 = pulse speed (higher = faster pulsing)
    # sin() gives -1 → 1, so:
    # +1.0 shifts it to 0 → 2
    # *0.5 scales it to 0 → 1
    # => p becomes a smooth looping value used for animation

    gr = view.scale(58 + int(18 * p))
    # 58 = base glow radius
    # 18 = how much the radius grows/shrinks
    # p (0→1) controls expansion, so radius = 58 → 76
    
    glow = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
    # creates transparent surface for glow
    # size = diameter (radius * 2), so glow always fits inside
    

    pygame.draw.circle(glow, (255, 230, 120, 18 + int(14 * p)), (gr, gr), gr)
    # outer glow layer
    # (255,230,120) = warm yellow color
    # 18 = minimum alpha (very faint)
    # 14 = additional brightness from pulse → alpha range: 18 → 32
    # (gr, gr) = center of surface
    # gr = radius (matches surface size)



    pygame.draw.circle(glow, (255, 230, 120, 34 + int(26 * p)), (gr, gr), max(view.scale(42), int(gr * 0.72)))
    # inner glow layer (brighter core)
    # 34 = base alpha
    # 26 = pulse intensity → alpha range: 34 → 60
    # radius = 72% of gr OR minimum 42 (prevents it from getting too small)

    screen.blit(glow, (cx - gr, cy - gr))
    # draws glow onto main screen
    # subtract gr to align glow center with (cx, cy)

    pygame.draw.circle(screen, (255, 230, 120), (cx, cy), view.scale(40))
    # solid center circle (core of beacon)
    # 40 = fixed radius (does not pulse, stays constant)
    # making it pulse would be nice
    
    # puts current night number on the top left of screen
    frame = view.content_rect()
    font = view.font(13, FONT_PATH)
    label = font.render(f"night {day_cycle.day}", True, (120, 110, 150))
    screen.blit(label, (frame.x + view.scale(20), frame.y + view.scale(20)))
    
    # load dialogues, later replace by tasks + dialogues ;)
    if not dialogue.active() and not done:
        script = constants.SCRIPTS.get(day_cycle.day, ["The dark holds its breath."])
        dialogue.show(script, style="thought")
    
    # draws player and dialogues on the screen
    player_rect = player.draw(screen, _player)
    dialogue.draw(screen, player_rect)
    
