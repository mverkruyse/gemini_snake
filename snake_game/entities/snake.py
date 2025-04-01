import pygame
import random
import math
from .. import settings as s
from .. import utils
# Import Hazard only needed if AI checks specific hazard types beyond collision
from .hazard import Hazard # If AI needs to know hazard.h_type

class Snake:
    def __init__(self, game, is_player=True, start_pos=None, direction=None):
        self.game = game # Store reference to the main game state object
        self.is_player = is_player

        if start_pos is None:
            start_x = s.GRID_WIDTH // 4 if is_player else s.GRID_WIDTH * 3 // 4
            start_y = s.GRID_HEIGHT // 2
            start_pos = (start_x, start_y)
        self.start_pos = start_pos # Store initial start position

        if direction is None:
            direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

        self.grid_pos = [start_pos]
        self.visual_pos = [utils.grid_to_screen(start_pos)] * s.SNAKE_START_LEN
        self.direction = direction
        self.next_direction = self.direction
        self.length = s.SNAKE_START_LEN
        self.timer = 0
        self.speed = s.SNAKE_SPEED_BASE if is_player else s.COMPETITOR_SPEED_BASE
        self.grow_pending = 0
        self.alive = True
        self.pulse_timer = random.random() * 2 * math.pi
        self.pulse_intensity = 0

        # Assign colors and power-up states based on type
        if is_player:
            self.head_color = s.SNAKE_HEAD_COLOR
            self.body_color_start = s.SNAKE_BODY_COLOR_START
            self.body_color_end = s.SNAKE_BODY_COLOR_END
            # Player specific power-up states
            self.phase_active = False
            self.magnet_active = False
            self.multiplier_active = False
            self.burst_active = False
            self.powerup_timers = {'phase': 0, 'magnet': 0, 'multiplier': 0, 'burst': 0}
        else:
            self.head_color = s.COMPETITOR_HEAD_COLOR
            self.body_color_start = s.COMPETITOR_BODY_COLOR_START
            self.body_color_end = s.COMPETITOR_BODY_COLOR_END
            self.powerup_timers = {} # AI doesn't use player powerups

    def reset(self):
        """Resets the snake to its starting state."""
        self.grid_pos = [self.start_pos]
        self.visual_pos = [utils.grid_to_screen(self.start_pos)] * s.SNAKE_START_LEN
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)]) # New random direction
        self.next_direction = self.direction
        self.length = s.SNAKE_START_LEN
        self.timer = 0
        self.grow_pending = 0
        self.alive = True
        self.pulse_timer = random.random() * 2 * math.pi # Reset pulse phase
        # Reset player-specific powerups
        if self.is_player:
             self.phase_active = False; self.magnet_active = False
             self.multiplier_active = False; self.burst_active = False
             self.powerup_timers = {'phase': 0, 'magnet': 0, 'multiplier': 0, 'burst': 0}


    def change_direction(self, new_direction):
        """Requests a change in direction for the next grid step."""
        # Prevent immediate 180 degree turns for both player and AI
        is_opposite = (new_direction[0] == -self.direction[0] and self.direction[0] != 0) or \
                      (new_direction[1] == -self.direction[1] and self.direction[1] != 0)
        if not is_opposite:
            self.next_direction = new_direction


    def update_ai(self):
        """AI logic to determine the competitor's next move."""
        if self.is_player or not self.alive: 
            return # Only run for living AI
        target_pos = None
        # Prioritize food
        if self.game.food:
            target_pos = self.game.food.grid_pos
        # Could add logic to target powerups or flee player later

        head_x, head_y = self.grid_pos[0]
        possible_moves = []

        # --- Evaluate Potential Moves ---
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            # Avoid instant 180 turns (redundant with check in change_direction, but safe)
            if dx == -self.direction[0] and dy == -self.direction[1]:
                 if self.direction != (0,0): # Allow if not moving yet
                     continue

            next_pos = (head_x + dx, head_y + dy)

            # --- Check Obstacles ---
            # Walls
            if not (0 <= next_pos[0] < s.GRID_WIDTH and 0 <= next_pos[1] < s.GRID_HEIGHT):
                continue
            # Self
            if next_pos in self.grid_pos[1:]:
                continue
             # Player Snake Body/Head
            if self.game.player_snake and self.game.player_snake.alive and next_pos in self.game.player_snake.grid_pos:
                continue
            # Hazards (Bombs)
            is_on_hazard = False
            for hazard in self.game.hazards:
                 # Only need to check collision for bomb type now
                if hazard.h_type == 'bomb' and hazard.collides_with(next_pos):
                     is_on_hazard = True
                     break
            if is_on_hazard:
                continue

            # Calculate distance to target (if exists)
            dist = float('inf')
            if target_pos:
                # Use Manhattan distance for simple grid movement cost
                dist = abs(next_pos[0] - target_pos[0]) + abs(next_pos[1] - target_pos[1])

            possible_moves.append(((dx, dy), dist))

        # --- Choose Best Move ---
        if possible_moves:
            # Sort moves by distance (ascending)
            possible_moves.sort(key=lambda item: item[1])
            best_move_dir, best_dist = possible_moves[0]

            # If multiple moves have the same best distance, prefer current direction if possible
            best_moves = [m for m in possible_moves if m[1] == best_dist]
            if len(best_moves) > 1:
                 current_dir_move = next((m for m in best_moves if m[0] == self.direction), None)
                 if current_dir_move:
                      self.change_direction(current_dir_move[0])
                      return

            # Otherwise, just take the first best move
            self.change_direction(best_move_dir)

        # --- Handle Being Trapped (No valid moves found) ---
        else:
             # AI is trapped, will likely die on next step. Keep current direction.
             # No change needed, it will attempt self.direction on next update.
             pass


    def update(self, dt):
        """Updates the snake's state (movement, collisions, etc.)."""
        if not self.alive: return

        # AI determines its next move before the timer check
        if not self.is_player:
            self.update_ai()

        # Adjust timer based on game speed multiplier (only affects player for now)
        effective_dt = dt * self.game.effective_speed_multiplier if self.is_player else dt
        self.timer += effective_dt

        # Update player power-up timers
        if self.is_player:
            for p_type in list(self.powerup_timers.keys()):
                 if self.powerup_timers[p_type] > 0:
                     self.powerup_timers[p_type] -= dt # Timers run on real time
                     if self.powerup_timers[p_type] <= 0:
                         self.deactivate_powerup(p_type)

        # Pulsing effect timer
        self.pulse_timer = (self.pulse_timer + dt * 5) % (2 * math.pi)
        self.pulse_intensity = (math.sin(self.pulse_timer) + 1) / 2

        # --- Logical Movement (Grid Update) ---
        if self.timer >= 1.0 / self.speed:
            self.timer = 0 # Reset timer

            # Apply burst if active (Player only)
            burst_steps = 1
            if self.is_player and self.burst_active:
                 burst_steps = 2
                 # Consider deactivating burst after use or consuming length here

            for _ in range(burst_steps):
                if not self.alive: break # Stop if died mid-burst

                self.direction = self.next_direction
                current_head_pos = self.grid_pos[0]
                new_head_pos = (current_head_pos[0] + self.direction[0],
                                current_head_pos[1] + self.direction[1])

                # --- Collision Detection ---
                # Wall Collision
                if not (0 <= new_head_pos[0] < s.GRID_WIDTH and 0 <= new_head_pos[1] < s.GRID_HEIGHT):
                    self.alive = False
                    if not self.is_player: print(f"DEBUG: AI snake hit wall. Coords={new_head_pos}. Returning NOW.")
                    if self.is_player: self.game.trigger_game_over("wall")
                    return # Stop processing movement

                # Self Collision (Check phase powerup for player)
                can_phase = self.is_player and self.phase_active
                if not can_phase and new_head_pos in self.grid_pos[1:]:
                    self.alive = False
                    if self.is_player: self.game.trigger_game_over("self")
                    return

                # Hazard Collision (Bombs only)
                for hazard in self.game.hazards:
                    # Only need to check collision for bomb type now
                    if hazard.h_type == 'bomb' and hazard.collides_with(new_head_pos):
                         self.alive = False
                         if self.is_player: self.game.trigger_game_over("hazard: bomb")
                         return

                # --- Snake vs Snake Collision ---
                # Determine the other snake
                other_snake = None
                if self.is_player:
                    other_snake = self.game.competitor_snake
                else: # If this is the competitor
                    other_snake = self.game.player_snake

                if other_snake and other_snake.alive:
                     # Head-on collision
                     if new_head_pos == other_snake.grid_pos[0]:
                          self.alive = False
                          other_snake.alive = False # Both die
                          # Trigger game over based on who initiated check (player always gets priority message)
                          if self.is_player: self.game.trigger_game_over("head-on collision")
                          # If AI check caused it, player still lost
                          else: self.game.trigger_game_over("head-on collision")
                          return
                     # Collision with other snake's body
                     elif new_head_pos in other_snake.grid_pos[1:]: # Check body only, head checked above
                          self.alive = False
                          if self.is_player: self.game.trigger_game_over("collision with competitor")
                          # No game over if AI hits player's body, AI just dies
                          return


                # --- Update Snake Position ---
                self.grid_pos.insert(0, new_head_pos) # Add new head position

                # --- Grow or Move Tail ---
                if self.grow_pending > 0:
                    self.grow_pending -= 1
                    # Add a new visual segment duplicating the last one initially
                    self.visual_pos.append(self.visual_pos[-1])
                else:
                    # Remove tail grid position only if not growing
                    if len(self.grid_pos) > self.length: # Safety check
                         self.grid_pos.pop()
                    # Visual tail removal handled by interpolation list adjustment

        # --- Visual Movement (Interpolation) ---
        target_visual_pos = [utils.grid_to_screen(p) for p in self.grid_pos]

        # Ensure visual_pos list has the correct length
        while len(self.visual_pos) < len(self.grid_pos):
             self.visual_pos.append(self.visual_pos[-1]) # Add duplicates if grown
        while len(self.visual_pos) > len(self.grid_pos):
             self.visual_pos.pop() # Remove if shrunk (shouldn't happen normally)

        # Interpolate each segment's visual position
        interp_factor = min(1.0, s.INTERPOLATION_SPEED * dt * s.FPS) # Clamp interpolation
        for i in range(len(self.visual_pos)):
             current_x, current_y = self.visual_pos[i]
             target_x, target_y = target_visual_pos[i]
             # Add wrap-around logic here if needed for interpolation
             new_x = utils.lerp(current_x, target_x, interp_factor)
             new_y = utils.lerp(current_y, target_y, interp_factor)
             self.visual_pos[i] = (new_x, new_y)


    def grow(self):
        """Increases the snake's target length."""
        self.grow_pending += 1
        self.length += 1 # Also update length state variable


    def activate_powerup(self, p_type):
        """Activates a power-up for the player snake."""
        if not self.is_player: return # Only player uses these
        self.powerup_timers[p_type] = s.POWERUP_DURATION # Use duration from settings
        if p_type == 'phase': self.phase_active = True
        if p_type == 'magnet': self.magnet_active = True
        if p_type == 'multiplier': self.multiplier_active = True
        if p_type == 'burst': self.burst_active = True


    def deactivate_powerup(self, p_type):
        """Deactivates a power-up for the player snake."""
        if not self.is_player: return
        if p_type in self.powerup_timers: # Ensure key exists
            self.powerup_timers[p_type] = 0 # Set timer to 0
            if p_type == 'phase': self.phase_active = False
            if p_type == 'magnet': self.magnet_active = False
            if p_type == 'multiplier': self.multiplier_active = False
            if p_type == 'burst': self.burst_active = False


    def draw(self, surface):
        """Draws the snake on the given surface."""
        if not self.alive or not self.visual_pos: return # Don't draw dead or empty snakes

        num_segments = len(self.visual_pos)

        # --- Draw Body Segments ---
        for i in range(num_segments - 1, 0, -1): # Draw tail first for overlap
            pos = self.visual_pos[i]
            scale = utils.get_perspective_scale(pos[1])
            segment_size = int(s.GRID_SIZE * 0.8 * scale)
            if segment_size < 1: continue

            t = i / max(1, num_segments - 1) # Normalized position in body
            # Interpolate color
            color_r = utils.lerp(self.body_color_start[0], self.body_color_end[0], t)
            color_g = utils.lerp(self.body_color_start[1], self.body_color_end[1], t)
            color_b = utils.lerp(self.body_color_start[2], self.body_color_end[2], t)
            segment_color = (int(color_r), int(color_g), int(color_b))

            # Calculate radii using perspective scale
            pulse_rad_add = int(self.pulse_intensity * s.GRID_SIZE * 0.1 * scale)
            glow_radius = max(1, (segment_size // 2) + pulse_rad_add + int(3*scale)) # Body glow radius
            base_radius = max(1, segment_size // 2 + int(self.pulse_intensity * s.GRID_SIZE * 0.05 * scale))

            glow_color = (*segment_color, 60) # Faint body glow

            try:
                # Draw glow (outer transparent circle)
                temp_surf_glow = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf_glow, glow_color, (glow_radius, glow_radius), glow_radius)
                surface.blit(temp_surf_glow, (pos[0] - glow_radius, pos[1] - glow_radius))
                # Draw main segment
                pygame.draw.circle(surface, segment_color, (int(pos[0]), int(pos[1])), base_radius)
            except pygame.error: pass


        # --- Draw Head ---
        head_pos = self.visual_pos[0]
        head_scale = utils.get_perspective_scale(head_pos[1])
        head_size = int(s.GRID_SIZE * 0.9 * head_scale)
        if head_size < 1: return # Skip drawing if too small

        pulse_rad_add_head = int(self.pulse_intensity * s.GRID_SIZE * 0.15 * head_scale)
        # --- Adjusted head glow radius calculation ---
        head_glow_radius = max(1, (head_size // 2) + pulse_rad_add_head + int(1*head_scale)) # Reduced padding
        # -------------------------------------------
        head_base_radius = max(1, head_size // 2 + int(self.pulse_intensity * s.GRID_SIZE * 0.08 * head_scale))

        # Pulsating Halo Alpha Calculation
        min_alpha = 40
        max_alpha = 140
        pulsating_alpha = int(utils.lerp(min_alpha, max_alpha, self.pulse_intensity))
        pulsating_alpha = max(0, min(255, pulsating_alpha)) # Clamp alpha
        head_glow_color = (*self.head_color[:3], pulsating_alpha) # Use self.head_color

        try:
            # Draw Head Glow (Halo)
            temp_surf_head_glow = pygame.Surface((head_glow_radius*2, head_glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf_head_glow, head_glow_color, (head_glow_radius, head_glow_radius), head_glow_radius)
            surface.blit(temp_surf_head_glow, (head_pos[0] - head_glow_radius, head_pos[1] - head_glow_radius))

            # Draw Head Base
            pygame.draw.circle(surface, self.head_color, (int(head_pos[0]), int(head_pos[1])), head_base_radius)

            # Draw Head Light Effect (Optional - currently commented out)
            # if self.is_player:
            #    light_radius = int(s.GRID_SIZE * 1.5 * head_scale) # Example: Reduced size
            #    if light_radius > 1:
            #        gradient_surf = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
            #        center = light_radius
            #        for i in range(light_radius, 0, -2):
            #             alpha = max(0, 30 - int(i / light_radius * 30)) # Example: Reduced opacity
            #             pygame.draw.circle(gradient_surf, (200, 220, 255, alpha), (center, center), i)
            #        surface.blit(gradient_surf, (head_pos[0] - center, head_pos[1] - center), special_flags=pygame.BLEND_RGBA_ADD)

        except pygame.error:
            pass # Ignore drawing errors if size is invalid