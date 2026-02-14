"""
Chain Hockey - Entry point for the game.
"""

import pygame
import sys
import time
from chainhockey.config_manager import ConfigManager
from chainhockey.game import ChainHockeyGame, GameState
from chainhockey.menu import (StartMenu, PauseMenu, OptionsMenu, MenuState,
                             ServerSelectionMenu, MultiplayerMenu, CreateRoomMenu, JoinRoomMenu)
from chainhockey.network_sync import NetworkSync
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
    
    # Network sync (will be initialized when needed)
    network_sync = None
    server_url = "ws://localhost:8765"  # Default
    server_selection_menu = None
    multiplayer_menu = None
    create_room_menu = None
    join_room_menu = None
    
    # Create menus with proper callbacks
    def set_state(new_state):
        previous_state[0] = game_state[0]
        game_state[0] = new_state
    
    def handle_create_room():
        """Handle creating a room"""
        nonlocal network_sync, create_room_menu, set_state
        if not network_sync:
            network_sync = NetworkSync(server_url)
            network_sync.start()
        
        # Wait for connection
        time.sleep(0.5)
        
        if network_sync.connected:
            network_sync.create_room()
            # Wait for response
            time.sleep(0.5)
            messages = network_sync.poll_messages()
            for msg_type, data in messages:
                if msg_type == 'room_created':
                    room_id = data.get('room_id')
                    # Create menu with room ID
                    create_room_menu = CreateRoomMenu(
                        screen,
                        room_id=room_id,
                        on_cancel=lambda: (network_sync.stop() if network_sync else None, set_state(MenuState.MULTIPLAYER)),
                        on_player_joined=lambda: (game.set_multiplayer(network_sync, is_host=True), set_state(MenuState.GAME))
                    )
                    set_state(MenuState.CREATE_ROOM)
                    return
            # Error creating room
            print("Failed to create room")
        else:
            print("Not connected to server")
    
    def handle_join_room(room_id: str):
        """Handle joining a room"""
        nonlocal network_sync, join_room_menu, set_state
        if not network_sync:
            network_sync = NetworkSync(server_url)
            network_sync.start()
        
        # Wait a bit for connection
        time.sleep(0.5)
        
        if network_sync.connected:
            network_sync.join_room(room_id)
            # Wait for response
            time.sleep(0.5)
            messages = network_sync.poll_messages()
            for msg_type, data in messages:
                if msg_type == 'room_joined':
                    # Successfully joined
                    game.set_multiplayer(network_sync, is_host=False)
                    set_state(MenuState.GAME)
                    return
                elif msg_type == 'error':
                    if join_room_menu:
                        join_room_menu.set_error(data.get('message', 'Failed to join room'))
            # If no response, show error
            if join_room_menu:
                join_room_menu.set_error("Failed to join room. Check room code.")
        else:
            if join_room_menu:
                join_room_menu.set_error("Not connected to server")
    
    def create_server_selection_menu():
        nonlocal server_selection_menu
        if not server_selection_menu:
            server_selection_menu = ServerSelectionMenu(
                screen,
                on_connect=lambda url: handle_server_connect(url),
                on_back=lambda: set_state(MenuState.START)
            )
        return server_selection_menu
    
    def handle_server_connect(url):
        nonlocal server_url
        server_url = url
        set_state(MenuState.MULTIPLAYER)
    
    def create_multiplayer_menu():
        nonlocal multiplayer_menu
        if not multiplayer_menu:
            multiplayer_menu = MultiplayerMenu(
                screen,
                on_create_room=lambda: handle_create_room(),
                on_join_room=lambda: set_state(MenuState.JOIN_ROOM),
                on_back=lambda: set_state(MenuState.START)
            )
        return multiplayer_menu
    
    def create_join_room_menu():
        nonlocal join_room_menu
        if not join_room_menu:
            join_room_menu = JoinRoomMenu(
                screen,
                on_join=lambda room_id: handle_join_room(room_id),
                on_back=lambda: set_state(MenuState.MULTIPLAYER)
            )
        return join_room_menu
    
    start_menu = StartMenu(
        screen,
        on_start=lambda: set_state(MenuState.GAME),
        on_options=lambda: set_state(MenuState.OPTIONS),
        on_exit=lambda: set_state(MenuState.EXIT),
        on_multiplayer=lambda: set_state(MenuState.SERVER_SELECT)
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
        elif state == MenuState.SERVER_SELECT:
            current_menu = create_server_selection_menu()
            game.state = GameState.MENU
        elif state == MenuState.MULTIPLAYER:
            current_menu = create_multiplayer_menu()
            game.state = GameState.MENU
        elif state == MenuState.CREATE_ROOM:
            if not create_room_menu:
                handle_create_room()
            if create_room_menu:
                current_menu = create_room_menu
                game.state = GameState.MENU
                # Check for player joined
                if network_sync:
                    messages = network_sync.poll_messages()
                    for msg_type, data in messages:
                        if msg_type == 'player_connected':
                            create_room_menu.set_player_joined(True)
                            # Auto-start game after short delay
                            time.sleep(1)
                            game.set_multiplayer(network_sync, is_host=True)
                            set_state(MenuState.GAME)
            else:
                current_menu = create_multiplayer_menu()
        elif state == MenuState.JOIN_ROOM:
            current_menu = create_join_room_menu()
            game.state = GameState.MENU
        elif state == MenuState.GAME:
            if game.state != GameState.PLAYING:
                if game.state == GameState.PAUSED:
                    # Resuming from pause - don't reset game, just resume timer
                    game.resume_timer()
                    # Clear paused screen
                    if hasattr(game, '_paused_screen'):
                        del game._paused_screen
                    game.state = GameState.PLAYING
                else:
                    # Starting new game
                    game.start_game()
                    game.state = GameState.PLAYING
            current_menu = None
        elif state == MenuState.PAUSE:
            if game.state == GameState.PLAYING:
                # Just paused
                game.pause_timer()
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
            
            # Handle game events (only when playing)
            if game.state == GameState.PLAYING:
                # Handle ESC key for pause
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game.state = GameState.PAUSED
                    set_state(MenuState.PAUSE)
                    continue  # Don't process this event further
                # Handle Space key
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if game.game_over:
                        game.reset_game()
                    elif game.puck:
                        game.puck.reset()
                    continue  # Don't process this event further
                # Handle ESC after game over
                if game.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game.state = GameState.MENU
                    set_state(MenuState.START)
                    continue  # Don't process this event further
            
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
                # Draw game first (frozen state), then pause menu overlay
                # Store the game screen when first paused to avoid redrawing
                if not hasattr(game, '_paused_screen'):
                    game.draw_game()
                    game._paused_screen = game.get_screen().copy()
                # Draw the stored screen
                game.get_screen().blit(game._paused_screen, (0, 0))
                current_menu.draw(game.get_screen())
            else:
                current_menu.draw()
                if hasattr(game, '_paused_screen'):
                    del game._paused_screen
        else:
            game.draw_game()
            if hasattr(game, '_paused_screen'):
                del game._paused_screen
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    # Cleanup
    if network_sync:
        network_sync.stop()
    
    # Quit
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
