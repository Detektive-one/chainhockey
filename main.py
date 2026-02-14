"""
Chain Hockey - Entry point for the game.
"""

import pygame
import sys
from chainhockey.config_manager import ConfigManager
from chainhockey.game import ChainHockeyGame, GameState
from chainhockey.menu import StartMenu, PauseMenu, OptionsMenu, MenuState
from chainhockey.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


def main():
    """Initialize and run the game"""
    pygame.init()
    
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chain Hockey - Meteor Hammer")
    clock = pygame.time.Clock()
    
    # Initialize config manager
    config_manager = ConfigManager()
    config_manager.load()
    
    # Create game instance
    game = ChainHockeyGame(config_manager.get_config())
    
    # Menu state - use a list to allow modification in closures
    game_state = [MenuState.START]
    previous_state = [MenuState.START]  # Track where we came from
    
    # Create menus with proper callbacks
    def set_state(new_state):
        previous_state[0] = game_state[0]
        game_state[0] = new_state
    
    start_menu = StartMenu(
        screen,
        on_start=lambda: set_state(MenuState.GAME),
        on_options=lambda: set_state(MenuState.OPTIONS),
        on_exit=lambda: set_state(MenuState.EXIT)
    )
    
    pause_menu = PauseMenu(
        screen,
        on_resume=lambda: set_state(MenuState.GAME),
        on_options=lambda: set_state(MenuState.OPTIONS),
        on_main_menu=lambda: set_state(MenuState.START)
    )
    
    def options_back():
        # Return to previous state (either START or PAUSE)
        if previous_state[0] == MenuState.START:
            set_state(MenuState.START)
        else:
            set_state(MenuState.PAUSE)
    
    options_menu = OptionsMenu(
        screen,
        config_manager,
        on_back=options_back
    )
    
    # Main loop
    running = True
    current_menu = None
    
    while running:
        state = game_state[0]
        
        # Handle state transitions
        if state == MenuState.START:
            current_menu = start_menu
            game.state = GameState.MENU
        elif state == MenuState.GAME:
            if game.state != GameState.PLAYING:
                game.start_game()
                game.state = GameState.PLAYING
            current_menu = None
        elif state == MenuState.PAUSE:
            game.state = GameState.PAUSED
            current_menu = pause_menu
        elif state == MenuState.OPTIONS:
            game.state = GameState.OPTIONS
            current_menu = options_menu
            # Update options menu config reference
            options_menu.config = config_manager.get_config()
        elif state == MenuState.EXIT:
            running = False
            break
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            
            # Handle game events
            if game.state == GameState.PLAYING:
                game.handle_events()
                # Check if game wants to pause
                if game.state == GameState.PAUSED:
                    set_state(MenuState.PAUSE)
            
            # Handle menu events
            if current_menu:
                if isinstance(current_menu, PauseMenu):
                    current_menu.handle_event(event)
                else:
                    current_menu.handle_event(event)
        
        # Update game
        if game.state == GameState.PLAYING:
            game.update_game()
        
        # Draw
        if current_menu:
            if isinstance(current_menu, PauseMenu):
                # Draw game first, then pause menu overlay
                game.draw_game()
                current_menu.draw(game.get_screen())
            else:
                current_menu.draw()
        else:
            game.draw_game()
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    # Quit
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
