import pygame
import sys # To ensure clean exit

# Import the main Game class from the game module
from .game import Game

def run_game():
    """Initializes Pygame and runs the main game loop."""
    # Note: Pygame initialization is now handled inside Game.__init__
    game_instance = Game()
    try:
        game_instance.run() # run() contains the main loop and pygame.quit()
    except Exception as e:
        print(f"\nAn error occurred during game execution: {e}")
        pygame.quit() # Ensure Pygame quits even if error happens in run loop
        sys.exit(1) # Exit with error code

if __name__ == "__main__":
    # This allows running the game directly using: python -m snake_game.main
    run_game()
    sys.exit(0) # Normal exit