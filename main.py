"""
Chain Hockey - Entry point for the game.
"""

import pygame
from chainhockey.game import ChainHockeyGame


def main():
    """Initialize and run the game"""
    pygame.init()
    game = ChainHockeyGame()
    game.run()


if __name__ == "__main__":
    main()
