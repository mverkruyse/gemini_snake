import pygame
import random
import math
import json
from os import path, makedirs # Import makedirs to create data directory

# Import settings and utilities
from . import settings as s
from . import utils

# Import entity classes using relative paths
from .entities.snake import Snake
from .entities.food import Food
from .entities.powerup import PowerUp
from .entities.hazard import Hazard
from .entities.particle import Particle

# Import graphics components
from .graphics.background import Background
from .graphics.ui import draw_player_hud, draw_menu_screen, draw_game_over_screen # Import specific UI functions

class Game:
    def __init__(self):
        """Initializes Pygame, game state, and loads resources."""
        pygame.mixer.pre_init(44100, -16, 2, 512) # Optimize buffer for less sound delay
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((s.WIDTH, s.HEIGHT))
        pygame.display.set_caption("Bio-luminescent Snake Battle")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "MENU" # MENU, PLAYING, GAME_OVER

        # Game elements
        self.player_snake = None
        self.competitor_snake = None
        self.food = None
        self.particles = []
        self.powerups = []
        self.hazards = []

        # Scoring and state
        self.score = 0
        self.high_score = self.load_highscore()
        self.combo_count = 0
        self.last_eat_time = 0
        self.combo_timer = 0
        self.frenzy_active = False
        self.frenzy_timer = 0
        self.effective_speed_multiplier = 1.0 # For player speed mods

        # Effects
        self.screen_shake_timer = 0
        self.screen_shake_intensity = 4

        # Graphics components
        self.background = Background()
        self._prepare_border_surface() # Create border overlay

        # Load sounds (placeholders - replace paths in settings.py)
        self.sounds = self._load_sounds()
        if self.sounds.get("ambient"):
            self.sounds["ambient"].play(loops=-1)
            self.sounds["ambient"].set_volume(0.3)


    def _prepare_border_surface(self):
        """Creates the reusable transparent border surface."""
        self.border_surface = pygame.Surface((s.WIDTH, s.HEIGHT), pygame.SRCALPHA)
        self.border_surface.fill((0,0,0,0)) # Fully transparent
        pygame.draw.rect(self.border_surface, s.BORDER_COLOR, (0, 0, s.WIDTH, s.HEIGHT), s.BORDER_THICKNESS)

    def _load_sounds(self):
        """Loads sound files specified in settings. Returns a dictionary."""
        sounds = {}
        sound_paths = { # Define sounds to load here
            "eat": getattr(s, 'SOUND_EAT_PATH', None),
            "powerup": getattr(s, 'SOUND_POWERUP_PATH', None),
            "gameover": getattr(s, 'SOUND_GAMEOVER_PATH', None),
            "ambient": getattr(s, 'SOUND_AMBIENT_PATH', None),
            # Add combo sounds if defined in settings
            **{f"combo_{i}": getattr(s, f'SOUND_COMBO_{i}_PATH', None) for i in range(1, 6)}
        }
        for name, file_path in sound_paths.items():
            if file_path and path.exists(file_path):
                try:
                    sounds[name] = pygame.mixer.Sound(file_path)
                except pygame.error as e:
                    print(f"Warning: Could not load sound '{file_path}': {e}")
            # elif file_path: # Only print warning if path was set but not found
                 # print(f"Warning: Sound file not found: '{file_path}'")
        return sounds

    def _play_sound(self, name):
        """Plays a sound from the loaded sounds dictionary if it exists."""
        if name in self.sounds:
            self.sounds[name].play()

    def load_highscore(self):
        """Loads the high score from the JSON file."""
        # Ensure data directory exists
        data_dir = path.dirname(s.HIGHSCORE_FILE)
        if data_dir and not path.exists(data_dir):
             try:
                 makedirs(data_dir)
             except OSError as e:
                 print(f"Warning: Could not create data directory '{data_dir}': {e}")

        if path.exists(s.HIGHSCORE_FILE):
            try:
                with open(s.HIGHSCORE_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get("highscore", 0)
            except (IOError, json.JSONDecodeError):
                print(f"Warning: Could not read or decode highscore file: {s.HIGHSCORE_FILE}")
                return 0
        return 0

    def save_highscore(self):
        """Saves the current high score to the JSON file."""
        # Ensure data directory exists
        data_dir = path.dirname(s.HIGHSCORE_FILE)
        if data_dir and not path.exists(data_dir):
             try:
                 makedirs(data_dir)
             except OSError as e:
                 print(f"Warning: Could not create data directory '{data_dir}': {e}")
                 # Optionally decide not to save if dir fails? For now, we proceed.

        try:
            with open(s.HIGHSCORE_FILE, 'w') as f:
                json.dump({"highscore": self.high_score}, f)
        except IOError:
            print(f"Warning: Could not save highscore to file: {s.HIGHSCORE_FILE}")

    def start_new_game(self):
        """Resets the game state for a new round."""
        self.score = 0
        # Create or reset snakes
        if self.player_snake is None:
             self.player_snake = Snake(self, is_player=True)
        else:
             self.player_snake.reset()

        if self.competitor_snake is None:
             self.competitor_snake = Snake(self, is_player=False)
        else:
             self.competitor_snake.reset()

        # Clear lists and reset state variables
        self.particles.clear()
        self.powerups.clear()
        self.hazards.clear()
        self.combo_count = 0
        self.last_eat_time = 0
        self.frenzy_active = False
        self.frenzy_timer = 0
        self.effective_speed_multiplier = 1.0
        self.screen_shake_timer = 0

        # Create initial food item *after* resetting snakes
        self.food = Food(self)

        self.game_state = "PLAYING"


    def trigger_game_over(self, reason="unknown"):
        """Transitions the game to the Game Over state."""
        if self.game_state == "PLAYING": # Prevent multiple triggers
            self.game_state = "GAME_OVER"
            self._play_sound("gameover")
            is_new_highscore = False
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_highscore()
                is_new_highscore = True # Flag for UI drawing
            self.screen_shake_timer = 0.5 # Trigger screen shake
            self.screen_shake_intensity = 8
            print(f"Game Over! Reason: {reason}, Score: {self.score}")
            # Store reason or new highscore flag if needed for drawing
            self.game_over_reason = reason
            self.is_new_highscore = is_new_highscore


    def spawn_particles(self, pos, count, color):
        """Spawns a number of particles at a given position."""
        for _ in range(count):
            self.particles.append(Particle(pos, color, life=random.uniform(0.5, 1.2)))


    def run(self):
        """The main game loop."""
        while self.running:
            # Calculate delta time for frame-independent physics/updates
            dt = self.clock.tick(s.FPS) / 1000.0

            # Process events, update game state, draw frame
            self.handle_events()
            self.update(dt)
            self.draw()

        # Clean up Pygame when loop exits
        pygame.quit()


    def handle_events(self):
        """Processes user input and game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                # Handle PLAYING state input
                if self.game_state == "PLAYING" and self.player_snake and self.player_snake.alive:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.player_snake.change_direction((0, -1))
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.player_snake.change_direction((0, 1))
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.player_snake.change_direction((-1, 0))
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.player_snake.change_direction((1, 0))
                    # Add keybinds for activating powerups if desired (e.g., space for burst)

                # Handle MENU/GAME_OVER state input
                elif self.game_state in ["GAME_OVER", "MENU"]:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.start_new_game() # Start/Restart
                    if event.key == pygame.K_ESCAPE:
                         self.running = False # Allow quitting from these states

                # Global quit key
                if event.key == pygame.K_ESCAPE and self.game_state == "PLAYING":
                     # Maybe pause instead? For now, just quit.
                     self.running = False


    def update(self, dt):
        """Updates all game logic and objects."""
        self.background.update(dt) # Update background animations

        if self.game_state != "PLAYING":
            return # Don't update game elements if not playing

        # --- Spawn Hazards & Powerups ---
        if random.random() < s.HAZARD_SPAWN_CHANCE * (1 + int(self.frenzy_active)):
             if len(self.hazards) < s.HAZARD_MAX_COUNT:
                 new_hazard = Hazard(self) # Pass self (game state)
                 if new_hazard.lifetime > 0: # Check if spawn was successful
                      self.hazards.append(new_hazard)

        if random.random() < s.POWERUP_SPAWN_CHANCE:
             if len(self.powerups) < s.POWERUP_MAX_COUNT:
                 # Pass self (game state) for spawn checks
                 self.powerups.append(PowerUp(self))


        # --- Update Hazard Speed Modifiers & Lifetime ---
        hazard_speed_modifier = 1.0
        if self.player_snake and self.player_snake.alive:
            current_snake_grid_pos = self.player_snake.grid_pos[0]
            # Note: Mist/Current speed logic remains but these types aren't spawned
            for hazard in self.hazards:
                if hazard.collides_with(current_snake_grid_pos):
                     if hazard.h_type == 'mist': hazard_speed_modifier *= 0.6
                     elif hazard.h_type == 'current': hazard_speed_modifier *= 1.5

        # Apply speed modifiers (including frenzy) to player snake
        self.effective_speed_multiplier = hazard_speed_modifier
        if self.frenzy_active:
             self.effective_speed_multiplier *= 1.3 # Base frenzy speedup

        # Update hazards and remove expired ones
        self.hazards = [h for h in self.hazards if h.update(dt)]


        # --- Update Frenzy Mode ---
        if self.frenzy_active:
            self.frenzy_timer -= dt
            if self.frenzy_timer <= 0:
                self.frenzy_active = False
                # Maybe play a "frenzy end" sound
            # Spawn extra food during frenzy
            if random.random() < 0.05: # Chance per frame
                if self.food: self.food.spawn() # Respawn existing food


        # --- Update Snakes ---
        if self.player_snake: self.player_snake.update(dt)
        if self.competitor_snake: self.competitor_snake.update(dt)


        # --- Check Food Collision ---
        eater = None
        if self.food: # Ensure food exists
            player_head = self.player_snake.grid_pos[0] if self.player_snake and self.player_snake.alive else None
            competitor_head = self.competitor_snake.grid_pos[0] if self.competitor_snake and self.competitor_snake.alive else None
            food_pos = self.food.grid_pos

            if player_head == food_pos:
                 eater = self.player_snake
            elif competitor_head == food_pos:
                 eater = self.competitor_snake

            if eater:
                eater.grow()
                self.spawn_particles(self.food.visual_pos, 20, s.FOOD_COLOR) # Use settings color
                self._play_sound("eat") # Play basic eat sound

                # Handle player-specific scoring and combo logic
                if eater.is_player:
                    base_score = 10
                    combo_bonus = self.combo_count * 5
                    multiplier = 2 if self.player_snake.multiplier_active else 1
                    self.score += (base_score + combo_bonus) * multiplier

                    # Combo Logic
                    current_time = pygame.time.get_ticks() / 1000.0
                    if current_time - self.last_eat_time <= s.COMBO_TIME_LIMIT:
                        self.combo_count += 1
                        # Play combo sound based on count (capped)
                        combo_sound_level = min(self.combo_count, 5) # Max level 5 for sound example
                        self._play_sound(f"combo_{combo_sound_level}") # Assumes sounds combo_1, combo_2... exist
                    else:
                        self.combo_count = 1 # Reset combo but count this eat

                    self.last_eat_time = current_time
                    self.combo_timer = s.COMBO_TIME_LIMIT # Reset visual timer

                    # Check for Frenzy Trigger
                    if not self.frenzy_active and self.combo_count >= s.FRENZY_THRESHOLD:
                        self.frenzy_active = True
                        self.frenzy_timer = s.FRENZY_DURATION
                        # Maybe play frenzy start sound

                # Respawn food after eaten
                self.food.spawn()


        # --- Update Combo Timer Decay ---
        if self.combo_timer > 0:
             self.combo_timer -= dt
             if self.combo_timer <= 0:
                 self.combo_count = 0 # Combo expired


        # --- Update Powerups & Check Player Collision/Magnet ---
        active_powerups = []
        collected_powerup = False
        if self.player_snake and self.player_snake.alive:
            player_head_grid = self.player_snake.grid_pos[0]
            for powerup in self.powerups:
                powerup.update(dt) # Update animation state if any
                if player_head_grid == powerup.grid_pos:
                    self.player_snake.activate_powerup(powerup.p_type)
                    self.spawn_particles(powerup.visual_pos, 15, powerup.color)
                    self._play_sound("powerup")
                    collected_powerup = True # Flag that one was collected
                    # Don't add collected powerup back to the list
                else:
                    active_powerups.append(powerup) # Keep uncollected ones
            if collected_powerup:
                self.powerups = active_powerups # Update list only if something changed

            # --- Update Orb Magnet Effect ---
            if self.player_snake.magnet_active and self.food:
                magnet_range_pixels = s.GRID_SIZE * s.MAGNET_RANGE_GRID
                magnet_radius_sq = magnet_range_pixels**2
                head_pos = self.player_snake.visual_pos[0]
                food_pos = list(self.food.visual_pos)
                dx, dy = head_pos[0] - food_pos[0], head_pos[1] - food_pos[1]
                dist_sq = dx*dx + dy*dy

                if 0 < dist_sq < magnet_radius_sq: # Check if within range
                    dist = math.sqrt(dist_sq)
                    normalized_dist = min(1.0, dist / magnet_range_pixels) # Clamp normalized distance
                    # Interpolate speed based on distance
                    move_speed = utils.lerp(s.MAGNET_PULL_SPEED_CLOSE, s.MAGNET_PULL_SPEED_FAR, normalized_dist)

                    # Calculate movement vector and apply
                    move_x = (dx / dist) * move_speed * dt
                    move_y = (dy / dist) * move_speed * dt
                    food_pos[0] += move_x
                    food_pos[1] += move_y
                    self.food.visual_pos = tuple(food_pos)
                    # Could add logic to snap food's grid_pos if visual pos gets very close


        # --- Update Particles ---
        # Filter out dead particles efficiently
        self.particles = [p for p in self.particles if p.life > 0]
        # Update remaining particles
        for p in self.particles:
            p.update(dt)


        # --- Update Screen Shake ---
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= dt


        # --- Check Player Death State ---
        # This check is redundant if trigger_game_over sets the state correctly,
        # but can be a failsafe. The primary transition happens in Snake.update.
        # if self.player_snake and not self.player_snake.alive:
        #      self.trigger_game_over("Eliminated")


    def draw(self):
        """Draws the entire game screen."""
        # --- Screen Shake Offset Calculation ---
        screen_offset_x, screen_offset_y = 0, 0
        # Apply shake only during game over transition for dramatic effect
        if self.screen_shake_timer > 0 and self.game_state == "GAME_OVER":
            intensity = self.screen_shake_intensity * (self.screen_shake_timer / 0.5) # Fade out shake
            screen_offset_x = random.randint(-int(intensity), int(intensity))
            screen_offset_y = random.randint(-int(intensity), int(intensity))

        # Use a temporary surface for shaking effect if needed
        # Note: This copy can impact performance. Only use if shaking.
        draw_surface = self.screen
        temp_surface = None
        if screen_offset_x != 0 or screen_offset_y != 0:
             # Create temp surface only when actually shaking
             temp_surface = self.screen.copy()
             draw_surface = temp_surface

        # --- Render Layers ---
        # 1. Background
        self.background.draw(draw_surface)

        # 2. Gameplay Elements (only if playing or game over)
        if self.game_state in ["PLAYING", "GAME_OVER"]:
            # Sort drawable entities roughly by Y for pseudo-depth
            drawable_entities = []
            drawable_entities.extend(self.hazards)
            if self.food: drawable_entities.append(self.food)
            drawable_entities.extend(self.powerups)
            if self.player_snake: drawable_entities.append(self.player_snake)
            if self.competitor_snake: drawable_entities.append(self.competitor_snake)

            # Define a function to get the primary Y coordinate for sorting
            def get_sort_y(entity):
                if isinstance(entity, Snake) and entity.visual_pos: return entity.visual_pos[0][1] # Sort by head Y
                elif hasattr(entity, 'visual_pos'): return entity.visual_pos[1] # Food, Powerup
                elif isinstance(entity, Hazard) and entity.grid_positions:
                    # Average Y of hazard grid positions
                    avg_y = sum(utils.grid_to_screen(gp)[1] for gp in entity.grid_positions) / len(entity.grid_positions)
                    return avg_y
                return s.HEIGHT # Default to bottom if no position found

            drawable_entities.sort(key=get_sort_y)

            # Draw sorted entities
            for entity in drawable_entities:
                 entity.draw(draw_surface) # Each entity handles its own drawing

            # Draw particles on top
            for p in self.particles:
                p.draw(draw_surface)

            # Draw Player HUD on top of gameplay elements
            draw_player_hud(draw_surface, self.score, self.high_score,
                            self.combo_count, self.combo_timer,
                            self.frenzy_active, self.frenzy_timer,
                            self.player_snake)


        # 3. Menu Screen
        elif self.game_state == "MENU":
            draw_menu_screen(draw_surface, self.high_score)


        # 4. Game Over Screen (draws overlay on top)
        if self.game_state == "GAME_OVER":
            # Pass score and whether it was a new highscore
            draw_game_over_screen(draw_surface, self.score, self.is_new_highscore)


        # 5. Border (draws on top of everything except maybe final shake blit)
        draw_surface.blit(self.border_surface, (0, 0))


        # --- Final Blit to Actual Screen ---
        # If we used a temporary surface for shaking, blit it to the screen now
        if temp_surface:
            self.screen.blit(temp_surface, (screen_offset_x, screen_offset_y))
        # Otherwise, draw_surface was self.screen, no extra blit needed unless logic changes

        # Update the display
        pygame.display.flip()