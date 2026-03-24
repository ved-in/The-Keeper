import pygame
import core.view as view
import ui.dialogue as dialogue
import constants

_has_rag = False
_font = None
_ready = False  # blocks input for one frame so the scene-switch keypress doesn't leak in

DUST_COLS = 6
DUST_ROWS = 4
_dust = []

RAG_X,  RAG_Y,  RAG_W,  RAG_H  = 300, 340, 30, 20
LENS_X, LENS_Y, LENS_W, LENS_H = 580, 260, 120, 90


def init():
    global _has_rag, _dust, _font, _ready
    _has_rag = False
    _ready = False
    _dust = [[True] * DUST_COLS for _ in range(DUST_ROWS)]
    _font = view.font(11)
    dialogue.clear()
    dialogue.show(
        ["The lens is thick with salt and grime.", "Find something to clean it with."],
        style="thought",
    )


def _rag_rect():
    return view.rect(RAG_X, RAG_Y, RAG_W, RAG_H)


def _lens_rect():
    return view.rect(LENS_X, LENS_Y, LENS_W, LENS_H)


def _dust_cell_rect(col, row):
    lr = _lens_rect()
    cw = lr.width  // DUST_COLS
    ch = lr.height // DUST_ROWS
    return pygame.Rect(lr.x + col * cw, lr.y + row * ch, cw, ch)


def _all_clean():
    return not any(cell for row in _dust for cell in row)


def _wipe_at(pos):
    for row in range(DUST_ROWS):
        for col in range(DUST_COLS):
            if _dust[row][col] and _dust_cell_rect(col, row).collidepoint(pos):
                _dust[row][col] = False
                return True
    return False


def handle_event(event):
    global _has_rag
    if not _ready:
        return

    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        if not dialogue.advance():
            if _all_clean():
                import scenes.nightfall as nightfall
                import core.game as game
                nightfall.notify_task_done()
                game.switch("nightfall")

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if dialogue.active():
            return
        if not _has_rag:
            if _rag_rect().collidepoint(event.pos):
                _has_rag = True
                dialogue.show(["You pick up the rag."], style="thought")
        else:
            if _lens_rect().collidepoint(event.pos):
                _wipe_at(event.pos)
                if _all_clean():
                    dialogue.show(
                        ["The lens is clear.", "The light will carry further tonight."],
                        style="thought",
                    )


def update(dt):
    global _ready
    _ready = True
    dialogue.update(dt)


def draw(screen):
    screen.fill(constants.SKY_COLORS["day"])

    # rag — hidden once picked up
    if not _has_rag:
        pygame.draw.rect(screen, (180, 160, 130), _rag_rect(), border_radius=3)
        if _font:
            label = _font.render("Rag", True, (240, 235, 210))
            r = _rag_rect()
            screen.blit(label, (r.centerx - label.get_width() // 2, r.top - label.get_height() - 4))

    # lens base
    pygame.draw.rect(screen, (200, 220, 240), _lens_rect(), border_radius=6)

    # dust cells on top
    for row in range(DUST_ROWS):
        for col in range(DUST_COLS):
            if _dust[row][col]:
                cell = _dust_cell_rect(col, row)
                dust_surf = pygame.Surface((cell.width, cell.height), pygame.SRCALPHA)
                dust_surf.fill((180, 160, 100, 160))
                screen.blit(dust_surf, cell)

    # lens label
    if _font:
        lr = _lens_rect()
        label = _font.render("Lens", True, (40, 40, 60))
        screen.blit(label, (lr.centerx - label.get_width() // 2, lr.top - label.get_height() - 4))


def draw_ui(screen):
    dialogue.draw(screen)