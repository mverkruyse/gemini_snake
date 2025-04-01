import pygame

# Screen Dimensions
WIDTH = 960
HEIGHT = 720
GRID_SIZE = 30
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 60

# Colors (Bio-luminescent Theme)
DARK_BG = (5, 10, 20)
SNAKE_HEAD_COLOR = (150, 255, 150)  # Bright green (Player)
SNAKE_BODY_COLOR_START = (80, 200, 80)
SNAKE_BODY_COLOR_END = (40, 100, 40)
COMPETITOR_HEAD_COLOR = (255, 150, 150) # Bright Red (Competitor)
COMPETITOR_BODY_COLOR_START = (200, 80, 80)
COMPETITOR_BODY_COLOR_END = (100, 40, 40)
FOOD_COLOR = (255, 180, 50)        # Orange glow
FOOD_GLOW_COLOR = (255, 180, 50, 100) # Semi-transparent glow
POWERUP_COLORS = {
    'phase': (150, 150, 255),   # Light blue
    'magnet': (255, 100, 255), # Pink/Purple
    'multiplier': (255, 255, 100), # Yellow
    'burst': (255, 100, 100),   # Red
}
HAZARD_BOMB_BODY_COLOR = (200, 50, 50)  # RED COLOR
HAZARD_BOMB_FUSE_COLOR = (180, 180, 100)
HAZARD_BOMB_SHINE_COLOR = (240, 240, 240)
HAZARD_MIST_COLOR = (100, 100, 150, 70) # Unused visually, kept for potential logic reuse
HAZARD_CURRENT_COLOR = (180, 220, 255, 50) # Unused visually, kept for potential logic reuse
PARTICLE_COLOR = (200, 220, 255)
UI_TEXT_COLOR = (220, 220, 240)
UI_SHADOW_COLOR = (30, 30, 50)
BORDER_COLOR = (150, 180, 220, 100) # Light blue, semi-transparent
BORDER_THICKNESS = 5

# Game Mechanics Settings
SNAKE_START_LEN = 3
SNAKE_SPEED_BASE = 10.5 # Updates per second (Increased Speed)
COMPETITOR_SPEED_BASE = 8 # AI snake speed
INTERPOLATION_SPEED = 0.3
COMBO_TIME_LIMIT = 2.0
FRENZY_THRESHOLD = 10
FRENZY_DURATION = 8.0
POWERUP_DURATION = 10.0
HAZARD_SPAWN_CHANCE = 0.005
HAZARD_LIFETIME_MIN = 5.0
HAZARD_LIFETIME_MAX = 15.0
HAZARD_MAX_COUNT = 5 # Limit number of hazards
POWERUP_SPAWN_CHANCE = 0.003
POWERUP_MAX_COUNT = 3 # Limit number of powerups
MAGNET_RANGE_GRID = 7 # Range in grid units
MAGNET_PULL_SPEED_CLOSE = 150 # Speed when very close
MAGNET_PULL_SPEED_FAR = 30 # Speed at max range

# Perspective Scaling
MIN_SCALE = 0.8
MAX_SCALE = 1.2

# File Paths (relative to project root often, adjust as needed)
ASSET_DIR = "assets" # Base asset directory name
HIGHSCORE_FILE = f"{ASSET_DIR}/data/snake_highscore.json"
FONT_NAME = None # Use default pygame font if None (or specify path like f"{ASSET_DIR}/fonts/your_font.ttf")
# Add paths for images/sounds if you load them, e.g.:
# BACKGROUND_IMG_PATH = f"{ASSET_DIR}/images/background.png"
# SOUND_EAT_PATH = f"{ASSET_DIR}/sounds/eat.wav"
