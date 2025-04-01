import pygame
from .. import settings as s
import random

# Cache fonts for performance
_font_cache = {}

def get_font(size, font_name=s.FONT_NAME):
    """Gets (or creates and caches) a pygame font object."""
    key = (font_name, size)
    if key not in _font_cache:
        try:
            _font_cache[key] = pygame.font.Font(font_name, size)
        except IOError: # Fallback to default font if specified one not found
             print(f"Warning: Font '{font_name}' not found. Using default.")
             _font_cache[key] = pygame.font.Font(None, size) # Use default pygame font
    return _font_cache[key]

def draw_text(surface, text, size, x, y, color=s.UI_TEXT_COLOR, shadow_color=s.UI_SHADOW_COLOR, font_name=s.FONT_NAME, center=False):
    """Draws text with an optional shadow."""
    font = get_font(size, font_name)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    # Draw shadow/outline slightly offset
    if shadow_color:
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect()
        shadow_offset_x = x + 1
        shadow_offset_y = y + 1
        if center:
            shadow_rect.center = (shadow_offset_x, shadow_offset_y)
        else:
            shadow_rect.topleft = (shadow_offset_x, shadow_offset_y)
        surface.blit(shadow_surface, shadow_rect)

    # Draw main text
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

# --- You could add more UI drawing functions here ---
# e.g., function to draw the entire HUD, progress bars, etc.

def draw_player_hud(surface, score, high_score, combo_count, combo_timer, frenzy_active, frenzy_timer, player_snake):
    """Draws the main gameplay HUD elements."""
    # Score and High Score
    score_text = f"Score: {score}"
    highscore_text = f"High Score: {high_score}"
    draw_text(surface, score_text, 28, 10, 10)
    # Correctly right-align high score
    font = get_font(28, s.FONT_NAME)
    highscore_width = font.size(highscore_text)[0]
    draw_text(surface, highscore_text, 28, s.WIDTH - highscore_width - 10, 10)

    # Combo Meter/Timer
    if combo_count > 0 and combo_timer > 0:
         combo_str = f"Combo: x{combo_count}"
         draw_text(surface, combo_str, 24, 10, 45, color=(255, 200, 100))
         # Draw combo timer bar
         bar_width = 100; bar_height = 10
         fill_width = int(bar_width * (combo_timer / s.COMBO_TIME_LIMIT))
         pygame.draw.rect(surface, (100, 100, 100), (10, 75, bar_width, bar_height))
         pygame.draw.rect(surface, (255, 200, 100), (10, 75, fill_width, bar_height))

    # Frenzy Timer
    if frenzy_active:
         frenzy_str = f"FRENZY!"
         frenzy_color = (255, 50 + int(random.random()*100), 50 + int(random.random()*100)) # Flickering
         draw_text(surface, frenzy_str, 36, s.WIDTH // 2, 20, color=frenzy_color, center=True)
         # Draw frenzy timer bar
         bar_width = 150; bar_height = 12
         fill_width = int(bar_width * (frenzy_timer / s.FRENZY_DURATION))
         bar_x = (s.WIDTH - bar_width) // 2
         pygame.draw.rect(surface, (100, 0, 0), (bar_x, 55, bar_width, bar_height))
         pygame.draw.rect(surface, frenzy_color, (bar_x, 55, fill_width, bar_height))

    # Active Powerups (Draw below combo/frenzy bars)
    if player_snake:
        y_offset = 95 # Start y-position for powerup text
        powerup_icon_size = 8
        for p_type, timer in player_snake.powerup_timers.items():
             if timer > 0:
                 icon_color = s.POWERUP_COLORS.get(p_type, (255,255,255)) # Default white if not found
                 text = f"{p_type.upper()}: {timer:.1f}s"
                 # Draw simple circle icon
                 pygame.draw.circle(surface, icon_color, (25, y_offset + (get_font(18).get_height()//2) ), powerup_icon_size)
                 draw_text(surface, text, 18, 45, y_offset, color=icon_color)
                 y_offset += 25 # Move down for next powerup

def draw_menu_screen(surface, high_score):
    """Draws the main menu."""
    draw_text(surface, "Bio-luminescent Snake", 64, s.WIDTH // 2, s.HEIGHT // 3, center=True)
    draw_text(surface, "Battle!", 48, s.WIDTH // 2, s.HEIGHT // 3 + 70, center=True)
    draw_text(surface, "Press SPACE or ENTER to Start", 32, s.WIDTH // 2, s.HEIGHT // 2 + 50, center=True)
    draw_text(surface, "Arrow Keys or WASD to Move", 22, s.WIDTH // 2, s.HEIGHT * 2 // 3 + 20, center=True)
    draw_text(surface, f"High Score: {high_score}", 26, s.WIDTH // 2, s.HEIGHT * 3 // 4 + 20, center=True)

def draw_game_over_screen(surface, score, is_new_highscore):
    """Draws the game over overlay and text."""
    # Semi-transparent overlay
    overlay = pygame.Surface((s.WIDTH, s.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0,0))

    draw_text(surface, "GAME OVER", 72, s.WIDTH // 2, s.HEIGHT // 3, color=(255, 80, 80), center=True)
    draw_text(surface, f"Final Score: {score}", 40, s.WIDTH // 2, s.HEIGHT // 2, center=True)
    if is_new_highscore:
         draw_text(surface, "New High Score!", 30, s.WIDTH // 2, s.HEIGHT // 2 + 50, color=(255, 255, 100), center=True)
    draw_text(surface, "Press SPACE or ENTER to Restart", 28, s.WIDTH // 2, s.HEIGHT * 2 // 3 + 20, center=True)