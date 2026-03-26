import pygame
import core.view as view


class Minigame:
    def __init__(self) -> None:
        self._task_complete_cb = None
        self._done = False
    
    def reset(self) -> None:
        self._done = False
    
    def complete(self) -> None:
        import systems.minigame_overlay as overlay
        if not overlay._done:
            overlay.notify_done()
        self._fire_task_complete()
    
    def set_task_complete_callback(self, fn) -> None:
        self._task_complete_cb = fn
    
    def _fire_task_complete(self) -> None:
        if self._task_complete_cb:
            self._task_complete_cb()
            self._task_complete_cb = None
        
    def draw_hint(self, screen, content_rect, text, color=(150, 146, 164), font_size=10) -> None:
        font = view.font(font_size, "assets/fonts/IMFellEnglish-Regular.ttf")
        surf = font.render(text, True, color)
        screen.blit(surf, (
            content_rect.centerx - surf.get_width() // 2,
            content_rect.bottom - surf.get_height() - view.scale(4),
        ))
        