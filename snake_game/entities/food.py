import pygame
import random
import math
from .. import settings as s
from .. import utils

class Food:
    def __init__(self, game):
        self.game = game # Store reference to game state
        self.spawn()

    def spawn(self):
        occupied_positions = set()
        if self.game.player_snake and self.game.player_snake.alive:
            occupied_positions.update(self.game.player_snake.grid_pos)
        if self.game.competitor_snake and self.game.competitor_snake.alive:
            occupied_positions.update(self.game.competitor_snake.grid_pos)
        for hazard in self.game.hazards:
            occupied_positions.update(hazard.grid_positions) # Correctly update from hazard sets
        occupied_positions.update(p.grid_pos for p in self.game.powerups)

        while True:
            self.grid_pos = (random.randrange(0, s.GRID_WIDTH), random.randrange(0, s.GRID_HEIGHT))
            if self.grid_pos not in occupied_positions:
                self.visual_pos = utils.grid_to_screen(self.grid_pos)
                break

    def draw(self, surface):
        screen_pos = self.visual_pos
        scale = utils.get_perspective_scale(screen_pos[1])
        radius = int(s.GRID_SIZE // 2 * scale)
        glow_radius = int(radius * 1.5)
        if radius < 1: return

        # Use COLOR constants from settings
        glow_color_base = s.FOOD_GLOW_COLOR
        glow_color = (*glow_color_base[:3], int(glow_color_base[3] * (scale/((s.MIN_SCALE+s.MAX_SCALE)/2))))

        try:
            temp_surf_glow = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf_glow, glow_color, (glow_radius, glow_radius), glow_radius)
            surface.blit(temp_surf_glow, (screen_pos[0] - glow_radius, screen_pos[1] - glow_radius))
            pygame.draw.circle(surface, s.FOOD_COLOR, screen_pos, radius)
        except pygame.error:
            pass # Ignore drawing errors if size is invalid