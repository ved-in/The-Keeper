import math
import pygame
import constants as const
import core.view as view

# dialogue state stays here so scenes only worry about timing and input
_lines =[]
_index = 0
_style = "thought"
_label = ""
_reveal = 0.0
_reveal_speed = 0.0
_time = 0.0
_line_time = 0.0
_sound_path = None
_loaded_sound_path = None # prevents reloading the same sound file multiple times
_type_sound = None
_type_channel = None
_word_index = -1
_word_cooldown_end = 0.0
_typing_word = False


# loads a fresh dialogue sequence and remembers how it should be drawn
def show(lines, style="thought", label="", reveal_speed=0.0, sound_path=None):
    global _lines, _index, _style, _label, _reveal_speed, _time, _sound_path
    _lines = list(lines)
    _index = 0
    _style = style
    _label = label
    _reveal_speed = reveal_speed
    _time = 0.0
    _sound_path = sound_path
    _reset_typing()
    _start_line()

    if active() and _uses_typewriter():
        _load_type_sound()


# clears the current dialogue so the scene can move on
def clear():
    global _lines, _index, _style, _label, _reveal, _reveal_speed, _time, _line_time, _sound_path
    _lines =[]
    _index = 0
    _style = "thought"
    _label = ""
    _reveal = 0.0
    _reveal_speed = 0.0
    _time = 0.0
    _line_time = 0.0
    _sound_path = None
    _reset_typing()


# true while we still have lines left to show
def active():
    return bool(_lines) and _index < len(_lines)


# handles reveal timing and the tiny typing sound loop
def update(dt):
    global _time, _line_time, _reveal
    if not active():
        return

    _time += dt
    _line_time += dt

    if _uses_typewriter():
        _reveal = min(_reveal + (dt * _reveal_speed), float(len(_current_line())))
        # dt = time passed since last frame
        # _reveal_speed = characters to reveal per second
        # dt * _reveal_speed = exact fraction of a character to add this frame
        # min() ensures we never reveal more characters than the line actually has

    _update_typing()


# jumps to the next line, or closes the sequence when nothing is left
def advance():
    global _index, _reveal
    if not active():
        return False

    # if typewriter is still typing, clicking advance skips to the end of the line
    if _can_finish_current_line():
        _reveal = float(len(_current_line()))
        _reset_typing()
        return True

    # if line is fully revealed, go to the next line
    if _index < len(_lines) - 1:
        _index += 1
        _reset_typing()
        _start_line()
        return True

    clear()
    return False


# scenes call this every frame and the module decides which look to use
def draw(screen, anchor_rect=None):
    if not active():
        return

    if _style == "log":
        _draw_log(screen)
    else:
        _draw_thought(screen, anchor_rect)


# opening uses the framed log panel near the bottom
def _draw_log(screen):
    cfg = const.LOG_DIALOGUE
    frame = view.content_rect()
    font = view.font(cfg["font_size"], const.FONT_PATH)
    hint_font = view.font(cfg["hint_font_size"], const.FONT_PATH)
    line = _current_line()
    text, count = _visible_text()
    
    fade = min(_line_time / cfg["fade_time"], 1.0)
    # _line_time = time elapsed since the current line appeared
    # cfg["fade_time"] = duration of the fade-in effect
    # min() caps the result at 1.0 so it stops fading once fully visible
    
    alpha = max(0, min(cfg["max_alpha"], int(cfg["max_alpha"] * fade)))
    # scales the maximum allowed alpha (transparency) by our fade percentage
    
    box = _log_box(frame, cfg)

    _draw_log_panel(screen, box, cfg)

    if _label:
        tag = hint_font.render(_label, True, const.LOG_COLORS["tag"])
        tag.set_alpha(alpha)
        screen.blit(tag, (box.x + view.scale(cfg["tag_x"]), box.y + view.scale(cfg["tag_y"])))

    last_rect = _draw_log_lines(screen, box, font, text, fade, alpha, cfg)
    _draw_log_prompt(screen, box, hint_font, line, count, last_rect, cfg)


def _log_box(frame, cfg):
    return pygame.Rect(
        frame.x + view.scale(cfg["side_margin"]),
        frame.bottom - view.scale(cfg["bottom_offset"]),
        frame.w - view.scale(cfg["side_margin"] * 2),
        view.scale(cfg["height"]),
    )


def _draw_log_panel(screen, box, cfg):
    radius = view.scale(cfg["corner_radius"])
    shadow = box.move(0, view.scale(cfg["shadow_y"]))
    
    pygame.draw.rect(screen, const.LOG_COLORS["shadow"], shadow, border_radius=radius)
    pygame.draw.rect(screen, const.LOG_COLORS["bg"], box, border_radius=radius)
    pygame.draw.rect(
        screen,
        const.LOG_COLORS["border"],
        box,
        width=max(1, view.scale(1)),
        border_radius=radius,
    )

    accent = pygame.Rect(box.x, box.y, box.w, view.scale(cfg["accent_h"]))
    pygame.draw.rect(
        screen,
        const.LOG_COLORS["accent"],
        accent,
        border_top_left_radius=radius,
        border_top_right_radius=radius,
    )


def _draw_log_lines(screen, box, font, text, fade, alpha, cfg):
    lines = _wrap(text, font, box.w - view.scale(cfg["text_wrap_pad"]))
    text_y = box.y + view.scale(cfg["text_y_with_label"] if _label else cfg["text_y"])
    last_rect = None

    for part in lines[:2]:
        glow = font.render(part, True, const.LOG_COLORS["text_glow"])
        glow.set_alpha(int(cfg["glow_alpha"] * fade))
        
        label = font.render(part, True, const.LOG_COLORS["text"])
        label.set_alpha(alpha)
        
        rect = label.get_rect(topleft=(box.x + view.scale(cfg["text_x"]), text_y))
        
        shadow = font.render(part, True, const.LOG_COLORS["shadow"])
        shadow.set_alpha(int(cfg["text_shadow_alpha"] * fade))

        # Rendering stack: 
        # 1. Draw glow slightly offset left and right
        # 2. Draw hard drop shadow slightly down and right
        # 3. Draw the crisp main text on top
        screen.blit(glow, (rect.x - 1, rect.y))
        screen.blit(glow, (rect.x + 1, rect.y))
        screen.blit(shadow, (rect.x + 1, rect.y + 1))
        screen.blit(label, rect)

        text_y += font.get_height() + view.scale(cfg["line_gap"])
        last_rect = rect

    return last_rect


def _draw_log_prompt(screen, box, hint_font, line, count, last_rect, cfg):
    prompt = hint_font.render(const.PROMPT_TEXT, True, const.LOG_COLORS["prompt"])
    prompt_rect = prompt.get_rect(
        bottomright=(box.right - view.scale(cfg["prompt_x"]), box.bottom - view.scale(cfg["prompt_y"]))
    )

    if _uses_typewriter() and count < len(line) and last_rect:
        # blinking caret indicating text is currently typing
        blink = 0.5 + (math.sin(_time * cfg["caret_speed"]) * 0.5)
        # _time = global dialogue time (constantly increasing)
        # caret_speed = pulse frequency
        # sin() gives -1 → 1, so:
        # * 0.5 scales it to -0.5 → 0.5
        # + 0.5 shifts it to 0.0 → 1.0
        # => blink becomes a smooth looping value from 0 to 1 for alpha transparency
        
        caret_h = last_rect.height - view.scale(cfg["caret_trim"])
        caret = pygame.Surface((view.scale(cfg["caret_w"]), caret_h), pygame.SRCALPHA)
        # Using Python's unpacking (*) to inject the RGB values from constants, then attaching the alpha
        caret.fill((*const.LOG_COLORS["text"], int(cfg["caret_alpha"] * blink)))
        screen.blit(caret, (last_rect.right + view.scale(cfg["caret_x"]), last_rect.centery - (caret_h // 2)))
        return

    # bouncing triangle indicating text is done and waiting for input
    blink = 0.5 + (math.sin(_time * cfg["hint_speed"]) * 0.5)
    hint = pygame.Surface((view.scale(cfg["hint_size"]), view.scale(cfg["hint_size"])), pygame.SRCALPHA)
    pygame.draw.polygon(
        hint,
        (*const.LOG_COLORS["text"], int(cfg["hint_alpha"] * blink)),
        [(0, 0), (view.scale(cfg["hint_size"]), view.scale(cfg["hint_size"] // 2)), (0, view.scale(cfg["hint_size"]))],
    )
    screen.blit(prompt, prompt_rect)
    screen.blit(hint, (prompt_rect.x - view.scale(cfg["hint_x"]), prompt_rect.centery - view.scale(cfg["hint_y"])))


# gameplay lines should feel like a thought drifting out of the player
def _draw_thought(screen, anchor_rect):
    cfg = const.THOUGHT_DIALOGUE
    frame = view.content_rect()
    font = view.font(cfg["font_size"], const.FONT_PATH)
    hint_font = view.font(cfg["hint_font_size"], const.FONT_PATH)
    text, _ = _visible_text()

    if anchor_rect is None:
        anchor_rect = _default_anchor(frame, cfg)

    padding_x = view.scale(cfg["padding_x"])
    padding_y = view.scale(cfg["padding_y"])
    line_gap = view.scale(cfg["line_gap"])
    max_box_w = view.scale(cfg["max_box_w"])
    
    lines = _wrap(text, font, max_box_w - (padding_x * 2))
    hint = hint_font.render(const.PROMPT_TEXT, True, const.THOUGHT_COLORS["prompt"])
    box, head_y, tail_y = _thought_box(frame, anchor_rect, lines, font, hint, cfg)

    radius = view.scale(cfg["corner_radius"])
    shadow = box.move(0, view.scale(cfg["shadow_y"]))
    
    pygame.draw.rect(screen, const.THOUGHT_COLORS["shadow"], shadow, border_radius=radius)
    pygame.draw.rect(screen, const.THOUGHT_COLORS["bg"], box, border_radius=radius)
    pygame.draw.rect(
        screen,
        const.THOUGHT_COLORS["border"],
        box,
        width=max(1, view.scale(1)),
        border_radius=radius,
    )

    _draw_thought_tail(screen, anchor_rect, box, head_y, tail_y, cfg)
    _draw_thought_text(screen, box, lines, font, hint, cfg)


def _default_anchor(frame, cfg):
    return pygame.Rect(
        frame.centerx - view.scale(cfg["fallback_anchor_x"]),
        frame.bottom - view.scale(cfg["fallback_anchor_bottom"]),
        view.scale(cfg["fallback_anchor_w"]),
        view.scale(cfg["fallback_anchor_h"]),
    )


def _thought_box(frame, anchor_rect, lines, font, hint, cfg):
    padding_x = view.scale(cfg["padding_x"])
    padding_y = view.scale(cfg["padding_y"])
    line_gap = view.scale(cfg["line_gap"])
    safe_margin = view.scale(cfg["safe_margin"])
    tail_gap = view.scale(cfg["tail_gap"])
    max_box_w = view.scale(cfg["max_box_w"])
    
    # Calculate box dimensions dynamically based on text content
    text_width = max((font.size(line)[0] for line in lines), default=0)
    text_height = (len(lines) * font.get_height()) + (max(0, len(lines) - 1) * line_gap)
    box_w = min(max_box_w, max(text_width, hint.get_width()) + (padding_x * 2))
    box_h = text_height + hint.get_height() + (padding_y * 2) + view.scale(cfg["extra_bottom"])
    
    box_x = _clamp(
        anchor_rect.centerx - (box_w // 2),
        frame.left + safe_margin,
        frame.right - safe_margin - box_w,
    )
    # anchor.centerx - (box_w // 2) tries to perfectly center the bubble above the anchor
    # frame.left + safe_margin = left screen boundary wall
    # frame.right - safe_margin - box_w = right screen boundary wall
    # _clamp() locks the bubble position so it never goes off-screen

    preferred_y = anchor_rect.top - box_h - tail_gap
    # Determine vertical position and tail orientation
    if preferred_y >= frame.top + safe_margin:
        # Place bubble above the anchor point
        box_y = preferred_y
        head_y = anchor_rect.top + view.scale(cfg["tail_head_offset"])
        tail_y = box_y + box_h + view.scale(cfg["tail_head_offset"])
    else:
        # Place bubble below the anchor point (if there's no room above)
        box_y = min(anchor_rect.bottom + tail_gap, frame.bottom - safe_margin - box_h)
        head_y = anchor_rect.bottom - view.scale(cfg["tail_head_offset"])
        tail_y = box_y - view.scale(cfg["tail_head_offset"])

    return pygame.Rect(box_x, box_y, box_w, box_h), head_y, tail_y


def _draw_thought_tail(screen, anchor_rect, box, head_y, tail_y, cfg):
    # the staggered circles keep it feeling like a thought bubble, not a speech box
    anchor_x = anchor_rect.centerx
    inset = view.scale(cfg["tail_inset"])
    tail_start_x = _clamp(anchor_x, box.left + inset, box.right - inset)
    tail_mid_x = int((tail_start_x + anchor_rect.centerx) * 0.5)
    tail_end_x = int((tail_start_x + (anchor_rect.centerx * 2)) / 3)
    
    tail_mid_y = int((tail_y + head_y) * cfg["tail_mid_ratio"])
    # cfg["tail_mid_ratio"] (usually around 0.55) finds a point slightly past the halfway mark
    # this causes the tiny trailing bubbles to visually curve instead of rendering in a straight, rigid line

    big_r, mid_r, small_r = (view.scale(radius) for radius in cfg["tail_radii"])
    tail_circles =[
        (tail_start_x, tail_y, big_r),   # largest circle near bubble
        (tail_mid_x, tail_mid_y, mid_r), # medium circle in middle
        (tail_end_x, head_y, small_r),   # smallest circle near character
    ]

    for x_pos, y_pos, radius in tail_circles:
        pygame.draw.circle(screen, const.THOUGHT_COLORS["shadow"], (x_pos, y_pos + view.scale(cfg["shadow_y"])), radius)
        pygame.draw.circle(screen, const.THOUGHT_COLORS["bg"], (x_pos, y_pos), radius)
        pygame.draw.circle(
            screen,
            const.THOUGHT_COLORS["border"],
            (x_pos, y_pos),
            radius,
            width=max(1, view.scale(1)),
        )


def _draw_thought_text(screen, box, lines, font, hint, cfg):
    padding_x = view.scale(cfg["padding_x"])
    padding_y = view.scale(cfg["padding_y"])
    line_gap = view.scale(cfg["line_gap"])
    text_y = box.top + padding_y

    for line in lines:
        label = font.render(line, True, const.THOUGHT_COLORS["text"])
        screen.blit(label, (box.left + padding_x, text_y))
        text_y += font.get_height() + line_gap

    hint_x = box.right - hint.get_width() - padding_x
    hint_y = box.bottom - hint.get_height() - padding_y
    screen.blit(hint, (hint_x, hint_y))


def _start_line():
    global _line_time, _reveal
    _line_time = 0.0
    if not active():
        _reveal = 0.0
    elif _uses_typewriter():
        _reveal = 0.0
    else:
        _reveal = float(len(_current_line()))


def _current_line():
    return _lines[_index]


# returns the portion of text that should currently be visible based on typewriter reveal
def _visible_text():
    line = _current_line()
    if not line:
        return "", 0

    if not _uses_typewriter():
        return line, len(line)

    count = min(len(line), max(1, int(_reveal)))
    # slices string from beginning up to the `count` index
    # eg. if count is 5, "Hello World" -> "Hello"
    return line[:count], count


def _uses_typewriter():
    return _reveal_speed > 0.0


def _can_finish_current_line():
    return _uses_typewriter() and int(_reveal) < len(_current_line())


# if the scene swaps sound files later, this makes sure we actually reload them
def _load_type_sound():
    global _type_sound, _type_channel, _loaded_sound_path
    if not _sound_path:
        return

    # only recreate the Sound object if the path has actually changed
    if _loaded_sound_path != _sound_path:
        _type_sound = None
        _loaded_sound_path = _sound_path

    if _type_sound is None:
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            _type_sound = pygame.mixer.Sound(_sound_path)
            _type_sound.set_volume(0.25)
        except pygame.error:
            _type_sound = None
            return

    if _type_channel is None:
        try:
            _type_channel = pygame.mixer.find_channel() or pygame.mixer.Channel(0)
        except pygame.error:
            _type_channel = None


# the sound follows whole words so it doesn't buzz every single frame
def _update_typing():
    global _word_index, _word_cooldown_end, _typing_word
    if not (_sound_path and _type_sound and _type_channel and active() and _uses_typewriter()):
        _stop_typing()
        _word_index = -1
        return

    _, count = _visible_text()
    current_idx = None
    word_end = 0

    # find which word the typewriter is currently revealing
    for idx, (start, end) in enumerate(_word_spans(_current_line())):
        if count > start and count <= end:
            current_idx = idx
            word_end = end
            break

    # if we are not inside a word, or line is finished, stop audio
    if current_idx is None or count >= len(_current_line()):
        _stop_typing()
        _word_index = -1
        return

    # reset tracking if we just moved to a brand new word
    if current_idx != _word_index:
        _word_index = current_idx
        _typing_word = False

    # if we are still typing the current word, play the loop
    if count < word_end:
        if not _typing_word and _time >= _word_cooldown_end:
            _type_channel.play(_type_sound, loops=-1)
            _typing_word = True
    else:
        # word finished typing, pause sound briefly to create natural speech gaps between words
        _stop_typing()
        _word_cooldown_end = _time + 0.06


# finds the start and end string indices for every word in a text line
# skips over spaces so we know precisely when actual letters are being drawn
def _word_spans(text):
    spans =[]
    in_word = False
    start_idx = 0

    for index, char in enumerate(text):
        if not char.isspace() and not in_word:
            start_idx = index
            in_word = True
        if in_word and char.isspace():
            spans.append((start_idx, index))
            in_word = False

    if in_word:
        spans.append((start_idx, len(text)))

    return spans


def _reset_typing():
    global _word_index, _word_cooldown_end
    _word_index = -1
    _word_cooldown_end = 0.0
    _stop_typing()


def _stop_typing():
    global _typing_word
    _typing_word = False
    if _type_channel:
        _type_channel.stop()


# automatically breaks long text strings into multiple lines
# so they fit within the max_width parameter
def _wrap(text, font, max_width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        test = f"{current} {word}"
        # measure the pixel width of the combined string
        if font.size(test)[0] <= max_width:
            # fits on the current line, append it
            current = test
        else:
            # exceeded max width, push current string to list and start a new line
            lines.append(current)
            current = word
    lines.append(current)
    return lines


# restricts a value within a minimum and maximum range
def _clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))
    # min(value, maximum) cuts off the value if it exceeds maximum
    # max(minimum, ...) cuts off the value if it drops below minimum