import pygame
import core.view as view
import core.minigame_overlay as overlay

TITLE = "Clean the Lens"

DUST_COLS = 7
DUST_ROWS = 4

_dust = []
_has_rag: bool = False
_dragging: bool = False


def reset() -> None:
    global _dust, _has_rag, _dragging
    _has_rag = False
    _dragging = False
    _dust = [[True] * DUST_COLS for _ in range(DUST_ROWS)]


def on_open() -> None:
    pass


def handle_event(event: pygame.event.Event) -> None:
    global _has_rag, _dragging
    
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        pos = event.pos
        if not _has_rag:
            if _rag_screen_rect() and _rag_screen_rect().collidepoint(pos):
                _has_rag = True
        else:
            if _lens_screen_rect() and _lens_screen_rect().collidepoint(pos):
                _dragging = True
                _wipe_at(pos)
            
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        _dragging = False
    if event.type == pygame.MOUSEMOTION:
        if _dragging and _has_rag:
            _wipe_at(event.pos)
            

def update(dt) -> None:
    if _all_clean() and not overlay._done:
        overlay.notify_done()
        _fire_task_complete()


_last_content_rect = None


def draw(screen: pygame.Surface, content_rect: pygame.Rect) -> None:
    global _last_content_rect
    _last_content_rect = content_rect

    font = view.font(10, "assets/fonts/IMFellEnglish-Regular.ttf")
    
    lr = _lens_screen_rect()
    pygame.draw.rect(screen, (190, 215, 235), lr, border_radius=view.scale(6))

    for row in range(DUST_ROWS):
        for col in range(DUST_COLS):
            if _dust[row][col]:
                cell = _dust_cell_screen_rect(col, row)
                if cell is None:
                    continue
                dust_surf = pygame.Surface((cell.width, cell.height), pygame.SRCALPHA)
                dust_surf.fill((180, 155, 90, 170))
                screen.blit(dust_surf, cell)
                
    pygame.draw.rect(screen, (120, 140, 160), lr, width=max(1, view.scale(1)), border_radius=view.scale(6))
    
    lbl = font.render("Lens", True, (50, 50, 70))
    screen.blit(lbl, (lr.centerx - lbl.get_width() // 2, lr.top - lbl.get_height() - view.scale(4)))
    
    if not _has_rag:
        hint = font.render("Pick up the rag first.", True, (150, 146, 164))
    elif not _all_clean():
        hint = font.render("Drag the rag across the lens to clean it.", True, (150, 146, 164))
    else:
        hint = font.render("Lens is clean!", True, (172, 200, 150))
        
    screen.blit(hint, (content_rect.centerx - hint.get_width() // 2, content_rect.bottom - hint.get_height() - view.scale(4)))
    
    if not _has_rag:
        rr = _rag_screen_rect()
        pygame.draw.rect(screen, (180, 160, 130), rr, border_radius=view.scale(3))
        lbl = font.render("Rag", True, (240, 235, 210))
        screen.blit(lbl, (rr.centerx - lbl.get_width() // 2, rr.top - lbl.get_height() - view.scale(4)))
    else:
        mx, my = pygame.mouse.get_pos()
        rw, rh = view.scale(28), view.scale(18)
        rag_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
        rag_surf.fill((180, 160, 130, 200))
        screen.blit(rag_surf, (mx - rw // 2, my - rh // 2))


def _rag_screen_rect():
    cr = _last_content_rect
    if cr is None:
        return None
    rw, rh = view.scale(36), view.scale(22)
    rx = cr.x + view.scale(24)
    ry = cr.centery - rh // 2
    return pygame.Rect(rx, ry, rw, rh)


def _lens_screen_rect():
    cr = _last_content_rect
    if cr is None:
        return None
    lw = int(cr.width * 0.55)
    lh = int(cr.height * 0.72)
    lx = cr.centerx - lw // 2 + view.scale(20)
    ly = cr.centery - lh // 2
    return pygame.Rect(lx, ly, lw, lh)


def _dust_cell_screen_rect(col: int, row: int):
    lr = _lens_screen_rect()
    if lr is None:
        return None
    cw = lr.width  // DUST_COLS
    ch = lr.height // DUST_ROWS
    return pygame.Rect(lr.x + col * cw, lr.y + row * ch, cw, ch)


def _all_clean() -> bool:
    return not any(cell for row in _dust for cell in row)


def _wipe_at(pos) -> None:
    for row in range(DUST_ROWS):
        for col in range(DUST_COLS):
            if _dust[row][col]:
                cell = _dust_cell_screen_rect(col, row)
                if cell and cell.collidepoint(pos):
                    _dust[row][col] = False




_task_complete_cb = None

def set_task_complete_callback(fn) -> None:
    global _task_complete_cb
    _task_complete_cb = fn

def _fire_task_complete() -> None:
    global _task_complete_cb
    if _task_complete_cb:
        _task_complete_cb()
        _task_complete_cb = None
        