# Bio-luminescent Snake Battle

A hyper-realistic Snake game clone with unique twists, built with Pygame. Features include a bio-luminescent theme, smooth movement, power-ups, hazards, a competitor AI, combos, and frenzy mode.

## Features

*   Bio-luminescent Mystical Forest theme
*   Smooth, interpolated snake movement
*   Competitor AI snake
*   Dynamic hazards (Bombs)
*   Power-ups (Phase, Magnet, Multiplier, Burst)
*   Combo and Frenzy modes
*   Particle effects
*   High score persistence
*   Pseudo-3D perspective scaling

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd bioluminescent-snake
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **(Optional) Place assets:** Add your own image, sound, and font files to the corresponding subdirectories within the `assets/` folder. Update file paths in `snake_game/settings.py` if necessary.

## Running the Game

```bash
python -m snake_game.main