import pygame
import random
import math
from .. import settings as s
from .. import utils

class Background:
    def __init__(self):
        self.scroll_speed_1 = 0.1 # Example parallax speeds
        self.scroll_speed_2 = 0.3
        self.offset_1 = 0
        self.offset_2 = 0
        self.fireflies = []
        for _ in range(100): # Number of fireflies
            self.fireflies.append({
                'pos': [random.uniform(0, s.WIDTH), random.uniform(0, s.HEIGHT)],
                'vel': [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)],
                'brightness': random.uniform(50, 150),
                'pulse_speed': random.uniform(1, 3),
                'pulse_offset': random.uniform(0, 2 * math.pi)
            })
        # Load background images here if using them
        # self.bg_image_1 = pygame.image.load(s.BACKGROUND_IMG_PATH_1).convert()
        # self.bg_image_1 = pygame.transform.scale(self.bg_image_1, (s.WIDTH, s.HEIGHT))
        # self.bg_image_2 = pygame.image.load(s.BACKGROUND_IMG_PATH_2).convert_alpha()
        # self.bg_image_2 = pygame.transform.scale(self.bg_image_2, (s.WIDTH, s.HEIGHT))


    def update(self, dt):
        # Update parallax offsets
        self.offset_1 = (self.offset_1 + self.scroll_speed_1 * dt * s.FPS) % s.WIDTH
        self.offset_2 = (self.offset_2 + self.scroll_speed_2 * dt * s.FPS) % s.WIDTH

        # Update fireflies
        for ff in self.fireflies:
            ff['pos'][0] = (ff['pos'][0] + ff['vel'][0] * dt * s.FPS) % s.WIDTH
            ff['pos'][1] = (ff['pos'][1] + ff['vel'][1] * dt * s.FPS) % s.HEIGHT
            # Randomly change direction slightly
            if random.random() < 0.01:
                 ff['vel'] = [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)]


    def draw(self, surface):
        surface.fill(s.DARK_BG)

        # Draw Parallax Layers (if images loaded)
        # surface.blit(self.bg_image_1, (self.offset_1, 0))
        # surface.blit(self.bg_image_1, (self.offset_1 - s.WIDTH, 0))
        # surface.blit(self.bg_image_2, (self.offset_2, 0))
        # surface.blit(self.bg_image_2, (self.offset_2 - s.WIDTH, 0))

        # Draw Procedural Fireflies
        current_time = pygame.time.get_ticks() / 1000.0
        for ff in self.fireflies:
            pulse = (math.sin(current_time * ff['pulse_speed'] + ff['pulse_offset']) + 1) / 2
            brightness = int(ff['brightness'] * pulse)
            scale = utils.get_perspective_scale(ff['pos'][1]) # Scale fireflies too
            size = int((2 + pulse * 2) * scale)
            if size < 1: continue

            color = (min(255, brightness + 50), min(255, brightness + 100), min(255, brightness), 150) # Yellowish glow

            try:
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, color, (size, size), size)
                # Use additive blending for brightness
                surface.blit(temp_surf, (int(ff['pos'][0] - size), int(ff['pos'][1] - size)), special_flags=pygame.BLEND_RGBA_ADD)
            except pygame.error:
                 pass # Ignore drawing error if size is invalid