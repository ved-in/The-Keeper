import pygame

# details about current dialogue
# _lines store the dialogue list, _index stores current index
_lines = []
_index = 0


# initializes _lines and _index
def show(lines):
    global _lines, _index
    _lines = lines
    _index = 0


# clears current dialogue list for the next one
def clear():
    global _lines, _index
    _lines = []
    _index = 0


# tells if current dialogue is active, or is completed
# returns true if dialogue sequence is in progress 
# returns false if _lines is empty or _index = len(_lines)
def active():
    return bool(_lines) and _index < len(_lines)


# advances to next dialogue line
def advance():
    global _index, _lines
    if _index < len(_lines) - 1:
        _index += 1
        return True
    clear()
    return False


def draw(screen):
    if not active():
        return
    
    # draws current dialogue on the screen with the font monospace.
    # I like monospace
    font = pygame.font.SysFont("monospace", 15)
    pygame.draw.rect(screen, (20, 18, 35), pygame.Rect(20, 430, 920, 90))
    screen.blit(font.render(_lines[_index], True, (230, 225, 210)), (36, 448))
