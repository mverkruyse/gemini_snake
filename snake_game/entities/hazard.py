import pygame
import random
from .. import settings as s
from .. import utils

class Hazard:
    def __init__(self, game): # Pass game state if needed for spawn checks
        self.game = game # Store reference to game state object
        self.h_type = 'bomb'
        self.size = 1 # Bombs are 1x1
        self.grid_positions = set()
        self.lifetime = random.uniform(s.HAZARD_LIFETIME_MIN, s.HAZARD_LIFETIME_MAX)
        self.age = 0
        self.spawn() # Attempt to spawn

    def spawn(self):
         # Build set of all occupied grid positions
         occupied_positions = set()
         if self.game.player_snake and self.game.player_snake.alive:
             occupied_positions.update(self.game.player_snake.grid_pos)
         if self.game.competitor_snake and self.game.competitor_snake.alive:
             occupied_positions.update(self.game.competitor_snake.grid_pos)
         if self.game.food: # Check if food exists
             occupied_positions.add(self.game.food.grid_pos)
         occupied_positions.update(p.grid_pos for p in self.game.powerups)
         # Could optionally check against other hazards here too

         attempts = 0
         while attempts < 50: # Limit attempts
            # Bombs are 1x1, so start_x/y is the position
            start_x = random.randrange(0, s.GRID_WIDTH)
            start_y = random.randrange(0, s.GRID_HEIGHT)
            potential_pos = (start_x, start_y)

            if potential_pos not in occupied_positions:
                 self.grid_positions = {potential_pos} # Set with one tuple
                 return # Success
            attempts += 1
         # Failed to find a spot after many attempts
         self.lifetime = 0 # Mark for immediate removal if spawn fails

    def update(self, dt):
        self.age += dt
        return self.age < self.lifetime # Return True if still alive

    def collides_with(self, grid_pos):
        return grid_pos in self.grid_positions

    def draw(self, surface):
        if not self.grid_positions: return # Cannot draw if not spawned

        alpha_multiplier = 1.0
        fade_time = 1.0
        if self.age < fade_time: alpha_multiplier = self.age / fade_time
        elif self.lifetime - self.age < fade_time: alpha_multiplier = (self.lifetime - self.age) / fade_time

        # Get the single position for the bomb
        pos = list(self.grid_positions)[0]

        screen_pos_center = utils.grid_to_screen(pos)
        scale = utils.get_perspective_scale(screen_pos_center[1])
        scaled_grid_size = int(s.GRID_SIZE * scale)
        if scaled_grid_size < 1: return

        bomb_center_x = screen_pos_center[0]
        bomb_center_y = screen_pos_center[1]
        bomb_radius = max(1, int(scaled_grid_size * 0.4)) # Body radius

        try:
            # Draw Bomb Body
            # Use COLOR constants from settings
            body_color = (*s.HAZARD_BOMB_BODY_COLOR, int(255 * alpha_multiplier))
            temp_surf = pygame.Surface((bomb_radius*2, bomb_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, body_color, (bomb_radius, bomb_radius), bomb_radius)
            surface.blit(temp_surf, (bomb_center_x - bomb_radius, bomb_center_y - bomb_radius))

            # Draw Fuse
            fuse_start_y = bomb_center_y - bomb_radius
            fuse_end_x = bomb_center_x + int(scaled_grid_size * 0.1)
            fuse_end_y = fuse_start_y - int(scaled_grid_size * 0.2)
            fuse_thickness = max(1, int(2*scale))
            fuse_color = (*s.HAZARD_BOMB_FUSE_COLOR, int(255*alpha_multiplier))
            pygame.draw.line(surface, fuse_color, (bomb_center_x, fuse_start_y), (fuse_end_x, fuse_end_y), fuse_thickness)

            # Draw Shine
            shine_radius = max(1, int(bomb_radius * 0.3))
            shine_offset_x = -int(bomb_radius * 0.4)
            shine_offset_y = -int(bomb_radius * 0.4)
            shine_pos = (bomb_center_x + shine_offset_x, bomb_center_y + shine_offset_y)
            shine_color = (*s.HAZARD_BOMB_SHINE_COLOR, int(200 * alpha_multiplier))
            temp_shine_surf = pygame.Surface((shine_radius*2, shine_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_shine_surf, shine_color, (shine_radius, shine_radius), shine_radius)
            surface.blit(temp_shine_surf, (shine_pos[0] - shine_radius, shine_pos[1] - shine_radius))

        except pygame.error: pass