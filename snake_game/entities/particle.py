import pygame
import random
import math
from .. import settings as s # Relative import for settings
from .. import utils       # Relative import for utils

class Particle:
    def __init__(self, pos, color, life, speed_range=(1, 5), size_range=(2, 5), gravity=0.1):
        self.pos = list(pos)
        self.color = color
        self.life = life
        self.max_life = life
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        self.vel = [math.cos(angle) * speed, math.sin(angle) * speed]
        self.initial_size = random.uniform(*size_range)
        self.size = self.initial_size
        self.gravity = gravity

    def update(self, dt):
        self.life -= dt
        self.vel[1] += self.gravity
        self.pos[0] += self.vel[0] * dt * s.FPS # Use FPS from settings
        self.pos[1] += self.vel[1] * dt * s.FPS
        self.size = self.initial_size * max(0, self.life / self.max_life) # Linear shrink

    def draw(self, surface):
        if self.life > 0 and self.size >= 1:
            scale = utils.get_perspective_scale(self.pos[1]) # Use utils function
            current_size = max(1, self.size * scale)
            radius = int(current_size / 2)
            if radius < 1: return

            alpha = int(150 * (self.life / self.max_life)**0.5) # Fade alpha non-linearly
            color = (*self.color[:3], max(0, min(255,alpha)))

            try:
                temp_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, color, (radius, radius), radius)
                # Use additive blending for glow effect
                surface.blit(temp_surf, (int(self.pos[0] - radius), int(self.pos[1] - radius)), special_flags=pygame.BLEND_RGBA_ADD)
            except pygame.error:
                 pass # Ignore if surface size invalid