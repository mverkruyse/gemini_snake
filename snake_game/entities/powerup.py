import pygame
import random
import math
from .. import settings as s
from .. import utils

class PowerUp:
    def __init__(self, game):
        self.game = game # Store reference to game state
        self.p_type = random.choice(list(s.POWERUP_COLORS.keys()))
        self.color = s.POWERUP_COLORS[self.p_type]
        self.spawn()
        self.pulse_timer = random.random() * 2 * math.pi

    def spawn(self):
         occupied_positions = set()
         if self.game.player_snake and self.game.player_snake.alive:
             occupied_positions.update(self.game.player_snake.grid_pos)
         if self.game.competitor_snake and self.game.competitor_snake.alive:
             occupied_positions.update(self.game.competitor_snake.grid_pos)
         for hazard in self.game.hazards:
             occupied_positions.update(hazard.grid_positions) # Correctly update from hazard sets
         if self.game.food:
             occupied_positions.add(self.game.food.grid_pos)
         # Avoid spawning on other existing powerups (excluding self if respawning)
         occupied_positions.update(p.grid_pos for p in self.game.powerups if p != self)

         while True:
            self.grid_pos = (random.randrange(0, s.GRID_WIDTH), random.randrange(0, s.GRID_HEIGHT))
            if self.grid_pos not in occupied_positions:
                self.visual_pos = utils.grid_to_screen(self.grid_pos)
                break

    def update(self, dt):
         self.pulse_timer = (self.pulse_timer + dt * 4) % (2 * math.pi)

    def draw(self, surface):
        screen_pos = self.visual_pos
        scale = utils.get_perspective_scale(screen_pos[1])
        radius = int(s.GRID_SIZE * 0.4 * scale)
        if radius < 1 : return

        pulse = (math.sin(self.pulse_timer) + 1) / 2 # 0 to 1
        current_radius = radius + int(pulse * 4 * scale)
        glow_radius = current_radius + int(5 * scale)
        glow_color = (*self.color, 120) # Use self.color

        try:
            temp_surf_glow = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf_glow, glow_color, (glow_radius, glow_radius), glow_radius)
            surface.blit(temp_surf_glow, (screen_pos[0] - glow_radius, screen_pos[1] - glow_radius))

            rect_size = int(current_radius * 1.5)
            rect = pygame.Rect(0, 0, rect_size, rect_size)
            rect.center = screen_pos
            pygame.draw.rect(surface, self.color, rect, border_radius=max(1, int(3*scale)))
        except pygame.error:
             pass # Ignore drawing errors if size is invalid