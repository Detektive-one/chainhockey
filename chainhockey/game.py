"""
Main game loop and game state management.
"""

import pygame
import sys
from enum import Enum
from typing import Optional
from .config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, GRAY,
    GOAL_COLOR, GOAL_LEFT_X, GOAL_RIGHT_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT,
    STRIKER_RADIUS, PUCK_RADIUS, PUCK_COLOR, PUCK_MASS,
    PLAYER1_SPAWN_X, PLAYER2_SPAWN_X, PLAYER_SPAWN_Y, CENTER_LINE_X
)
from .chain import Chain
from .game_objects import Striker, Hammer, Puck
from .physics import check_collision_circle, resolve_collision, separate_circles
from .config_manager import GameConfig
from .network import NetworkClient, ConnectionState
from .network_sync import NetworkSync


class GameState(Enum):
    """Game state enumeration"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    OPTIONS = "options"


class ChainHockeyGame:
    """Main game class managing the game loop and state"""
    
    def __init__(self, config: GameConfig):
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chain Hockey - Meteor Hammer")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Store config
        self.config = config
        
        # Game state
        self.state = GameState.MENU
        self.running = True
        self.dt = 1.0  # Delta time for physics
        
        # Network/multiplayer
        self.network_sync: Optional[NetworkSync] = None
        self.is_multiplayer = False
        self.is_host = False  # Player 1 is host in multiplayer
        self.remote_player_input = {}  # Store remote player input
        self.last_state_send_time = 0
        self.state_send_interval = 100  # Send state every 100ms
        
        # Initialize game objects (will be created in start_game)
        self.striker1 = None
        self.striker2 = None
        self.chain1 = None
        self.chain2 = None
        self.hammer1 = None
        self.hammer2 = None
        self.puck = None
        self.player1_score = 0
        self.player2_score = 0
        self.goal_delay = 0
        self.game_over = False
        self.winner = None
        self.start_time = 0
        self.game_duration_ms = 0
        self.paused_time = 0
        self.pause_start_time = 0
        self.player1_min_x = 0
        self.player1_max_x = 0
        self.player2_min_x = 0
        self.player2_max_x = 0
    
    def start_game(self):
        """Initialize game objects with current config"""
        p1_config = self.config.player1
        p2_config = self.config.player2
        
        # Player boundaries
        # Player 1 (right side) can move from center to right edge
        self.player1_min_x = CENTER_LINE_X + p1_config.striker_radius
        self.player1_max_x = SCREEN_WIDTH - p1_config.striker_radius
        # Player 2 (left side) can move from left edge to center
        self.player2_min_x = p2_config.striker_radius
        self.player2_max_x = CENTER_LINE_X - p2_config.striker_radius
        
        # Create Player 1 (right side, mouse controlled)
        self.striker1 = Striker(PLAYER1_SPAWN_X, PLAYER_SPAWN_Y, 
                               p1_config.striker_radius, p1_config.striker_color,
                               self.player1_min_x, self.player1_max_x, 
                               is_player1=True, speed=p1_config.striker_speed)
        self.striker1.vel_x = 0
        self.striker1.vel_y = 0
        self.striker1.prev_x = self.striker1.x
        self.striker1.prev_y = self.striker1.y
        
        # Create Player 2 (left side, WASD controlled)
        self.striker2 = Striker(PLAYER2_SPAWN_X, PLAYER_SPAWN_Y,
                               p2_config.striker_radius, p2_config.striker_color,
                               self.player2_min_x, self.player2_max_x, 
                               is_player1=False, speed=p2_config.striker_speed)
        self.striker2.vel_x = 0
        self.striker2.vel_y = 0
        self.striker2.prev_x = self.striker2.x
        self.striker2.prev_y = self.striker2.y
        
        # Create chains with config values
        self.chain1 = Chain(self.striker1.x, self.striker1.y, p1_config.chain_color,
                           segments=p1_config.chain_segments,
                           segment_length=p1_config.segment_length,
                           thickness=p1_config.chain_thickness)
        self.chain2 = Chain(self.striker2.x, self.striker2.y, p2_config.chain_color,
                           segments=p2_config.chain_segments,
                           segment_length=p2_config.segment_length,
                           thickness=p2_config.chain_thickness)
        
        # Create hammers
        hammer1_x, hammer1_y = self.chain1.get_hammer_position()
        self.hammer1 = Hammer(hammer1_x, hammer1_y, p1_config.hammer_radius, 
                              p1_config.hammer_color,
                              self.player1_min_x, self.player1_max_x)
        hammer2_x, hammer2_y = self.chain2.get_hammer_position()
        self.hammer2 = Hammer(hammer2_x, hammer2_y, p2_config.hammer_radius,
                              p2_config.hammer_color,
                              self.player2_min_x, self.player2_max_x)
        
        # Create puck
        self.puck = Puck(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                        PUCK_RADIUS, PUCK_COLOR,
                        friction=self.config.puck_friction,
                        wall_bounce=self.config.puck_wall_bounce)
        
        # Reset game state
        self.player1_score = 0
        self.player2_score = 0
        self.goal_delay = 0
        self.game_over = False
        self.winner = None
        self.start_time = pygame.time.get_ticks()
        self.game_duration_ms = self.config.game_duration_seconds * 1000
        self.paused_time = 0
        self.pause_start_time = 0
    
    def reset_game(self):
        """Reset game state without reinitializing display"""
        self.start_game()
    
    def set_multiplayer(self, network_sync: NetworkSync, is_host: bool):
        """Enable multiplayer mode with network sync"""
        self.network_sync = network_sync
        self.is_multiplayer = True
        self.is_host = is_host
    
    def _process_network_messages(self):
        """Process network messages (call from main loop)"""
        if not self.network_sync:
            return
        
        # Poll for messages
        messages = self.network_sync.poll_messages()
        for msg_type, data in messages:
            if msg_type == 'player_connected':
                # Player 2 joined, can start game
                pass
            elif msg_type == 'player_disconnected':
                print(f"Player {data.get('player_num')} disconnected")
            elif msg_type == 'error':
                print(f"Network error: {data.get('message')}")
        
        # Poll for remote input
        inputs = self.network_sync.poll_input()
        for input_data in inputs:
            player_num = input_data.get('player_num')
            input_dict = input_data.get('input', {})
            self.remote_player_input[player_num] = input_dict
        
        # Poll for remote state (non-host only)
        if not self.is_host:
            states = self.network_sync.poll_state()
            for state_data in states:
                # Could apply remote state for reconciliation
                pass
    
    def _send_player_input(self):
        """Send local player input to network"""
        if not self.network_sync or not self.is_multiplayer:
            return
        
        # Get current input state
        mouse_x, mouse_y = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        
        input_data = {
            'mouse_x': mouse_x,
            'mouse_y': mouse_y,
            'keys': {
                'w': bool(keys[pygame.K_w]),
                'a': bool(keys[pygame.K_a]),
                's': bool(keys[pygame.K_s]),
                'd': bool(keys[pygame.K_d])
            }
        }
        
        # Send input (thread-safe)
        self.network_sync.send_input(input_data)
    
    def _send_game_state(self):
        """Send game state to network (host only)"""
        if not self.network_sync or not self.is_multiplayer or not self.is_host:
            return
        
        if not self.network_sync.connected:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_state_send_time < self.state_send_interval:
            return
        
        self.last_state_send_time = current_time
        
        # Prepare game state
        state = {
            'puck': {
                'x': self.puck.x if self.puck else 0,
                'y': self.puck.y if self.puck else 0,
                'vel_x': self.puck.vel_x if self.puck else 0,
                'vel_y': self.puck.vel_y if self.puck else 0
            },
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'time_remaining': self.get_time_remaining(),
            'game_over': self.game_over
        }
        
        # Send state (thread-safe)
        self.network_sync.send_state(state)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        # Pause the game
                        self.state = GameState.PAUSED
                        return True  # Signal that pause was triggered
                    elif self.game_over:
                        # After game over, ESC returns to menu
                        self.state = GameState.MENU
                        return True
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.PLAYING:
                        if self.game_over:
                            # Restart game
                            self.reset_game()
                        else:
                            # Reset puck position on spacebar
                            if self.puck:
                                self.puck.reset()
        return False
    
    def check_win_condition(self):
        """Check if game should end (5 minutes or 10 goals)"""
        if self.game_over:
            return
        
        # Check goal limit
        if self.player1_score >= self.config.max_goals:
            self.game_over = True
            self.winner = 1
            return
        if self.player2_score >= self.config.max_goals:
            self.game_over = True
            self.winner = 2
            return
        
        # Check time limit
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time >= self.game_duration_ms:
            self.game_over = True
            # Winner is player with more goals, or None if tie
            if self.player1_score > self.player2_score:
                self.winner = 1
            elif self.player2_score > self.player1_score:
                self.winner = 2
            else:
                self.winner = 0  # Tie
            return
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        # Process network messages
        if self.is_multiplayer:
            self._process_network_messages()
        
        # Handle multiplayer input
        if self.is_multiplayer:
            # Player 1: local input (mouse)
            if self.is_host or (not self.is_host and self.network_sync and self.network_sync.player_num == 1):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.striker1.prev_x = self.striker1.x
                self.striker1.prev_y = self.striker1.y
                self.striker1.update_position_mouse(mouse_x, mouse_y)
                self.striker1.vel_x = self.striker1.x - self.striker1.prev_x
                self.striker1.vel_y = self.striker1.y - self.striker1.prev_y
                # Send input to network
                self._send_player_input()
            else:
                # Apply remote input for Player 1
                if 1 in self.remote_player_input:
                    remote_input = self.remote_player_input[1]
                    self.striker1.prev_x = self.striker1.x
                    self.striker1.prev_y = self.striker1.y
                    self.striker1.update_position_mouse(remote_input.get('mouse_x', self.striker1.x),
                                                       remote_input.get('mouse_y', self.striker1.y))
                    self.striker1.vel_x = self.striker1.x - self.striker1.prev_x
                    self.striker1.vel_y = self.striker1.y - self.striker1.prev_y
            
            # Player 2: local or remote input
            if (not self.is_host and self.network_sync and self.network_sync.player_num == 2) or \
               (self.is_host and not self.is_multiplayer):
                # Local WASD control
                keys = pygame.key.get_pressed()
                self.striker2.prev_x = self.striker2.x
                self.striker2.prev_y = self.striker2.y
                self.striker2.update_position_keyboard(keys)
                self.striker2.vel_x = self.striker2.x - self.striker2.prev_x
                self.striker2.vel_y = self.striker2.y - self.striker2.prev_y
                # Send input to network
                if self.is_multiplayer:
                    self._send_player_input()
            else:
                # Apply remote input for Player 2
                if 2 in self.remote_player_input:
                    remote_input = self.remote_player_input[2]
                    keys_dict = remote_input.get('keys', {})
                    # Create a mock keys object
                    class MockKeys:
                        def __getitem__(self, key):
                            if key == pygame.K_w:
                                return keys_dict.get('w', False)
                            elif key == pygame.K_a:
                                return keys_dict.get('a', False)
                            elif key == pygame.K_s:
                                return keys_dict.get('s', False)
                            elif key == pygame.K_d:
                                return keys_dict.get('d', False)
                            return False
                    mock_keys = MockKeys()
                    self.striker2.prev_x = self.striker2.x
                    self.striker2.prev_y = self.striker2.y
                    self.striker2.update_position_keyboard(mock_keys)
                    self.striker2.vel_x = self.striker2.x - self.striker2.prev_x
                    self.striker2.vel_y = self.striker2.y - self.striker2.prev_y
        else:
            # Single player mode (original behavior)
            # Get mouse position and update Player 1 (mouse controlled)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.striker1.prev_x = self.striker1.x
            self.striker1.prev_y = self.striker1.y
            self.striker1.update_position_mouse(mouse_x, mouse_y)
            self.striker1.vel_x = self.striker1.x - self.striker1.prev_x
            self.striker1.vel_y = self.striker1.y - self.striker1.prev_y
            
            # Update Player 2 (WASD controlled)
            keys = pygame.key.get_pressed()
            self.striker2.prev_x = self.striker2.x
            self.striker2.prev_y = self.striker2.y
            self.striker2.update_position_keyboard(keys)
            self.striker2.vel_x = self.striker2.x - self.striker2.prev_x
            self.striker2.vel_y = self.striker2.y - self.striker2.prev_y
        
        # Update chain physics
        p1_config = self.config.player1
        p2_config = self.config.player2
        self.chain1.update(self.dt, self.striker1.x, self.striker1.y, 
                          self.striker1.radius, self.player1_min_x, self.player1_max_x,
                          damping=p1_config.chain_damping,
                          gravity=self.config.gravity,
                          constraint_iterations=self.config.constraint_iterations)
        self.chain2.update(self.dt, self.striker2.x, self.striker2.y,
                          self.striker2.radius, self.player2_min_x, self.player2_max_x,
                          damping=p2_config.chain_damping,
                          gravity=self.config.gravity,
                          constraint_iterations=self.config.constraint_iterations)
        
        # Update hammer positions based on chains
        hammer1_x, hammer1_y = self.chain1.get_hammer_position()
        self.hammer1.update_position(hammer1_x, hammer1_y)
        hammer2_x, hammer2_y = self.chain2.get_hammer_position()
        self.hammer2.update_position(hammer2_x, hammer2_y)
        
        # Update puck physics and check for goals
        if self.goal_delay > 0:
            self.goal_delay -= 1
        else:
            goal_result = self.puck.update()
            
            # Check if a goal was scored
            if goal_result == 'left':
                self.player2_score += 1
                self.puck.reset()
                self.goal_delay = 60  # 1 second delay at 60 FPS
            elif goal_result == 'right':
                self.player1_score += 1
                self.puck.reset()
                self.goal_delay = 60  # 1 second delay at 60 FPS
        
        # Handle collisions
        self.handle_collisions()
        
        # Check win conditions
        self.check_win_condition()
        
        # Send game state in multiplayer (host only)
        if self.is_multiplayer:
            self._send_game_state()
    
    def handle_collisions(self):
        """Handle collisions between game objects"""
        # Collision detection: Puck vs Hammer 1
        if check_collision_circle(self.puck.x, self.puck.y, self.puck.radius, 
                                 self.hammer1.x, self.hammer1.y, self.hammer1.radius):
            # Separate objects first
            self.puck.x, self.puck.y, hammer_x, hammer_y = separate_circles(
                self.puck.x, self.puck.y, self.puck.radius,
                self.hammer1.x, self.hammer1.y, self.hammer1.radius
            )
            
            # Resolve collision with momentum transfer
            p1_config = self.config.player1
            self.puck.vel_x, self.puck.vel_y, _, _ = resolve_collision(
                self.puck.x, self.puck.y, self.puck.vel_x, self.puck.vel_y, 
                self.puck.radius, PUCK_MASS,
                self.hammer1.x, self.hammer1.y, self.hammer1.vel_x, self.hammer1.vel_y, 
                self.hammer1.radius, p1_config.hammer_mass,
                restitution=1.2  # High restitution for hammer (power hit)
            )
        
        # Collision detection: Puck vs Hammer 2
        if check_collision_circle(self.puck.x, self.puck.y, self.puck.radius, 
                                 self.hammer2.x, self.hammer2.y, self.hammer2.radius):
            # Separate objects first
            self.puck.x, self.puck.y, hammer_x, hammer_y = separate_circles(
                self.puck.x, self.puck.y, self.puck.radius,
                self.hammer2.x, self.hammer2.y, self.hammer2.radius
            )
            
            # Resolve collision with momentum transfer
            p2_config = self.config.player2
            self.puck.vel_x, self.puck.vel_y, _, _ = resolve_collision(
                self.puck.x, self.puck.y, self.puck.vel_x, self.puck.vel_y, 
                self.puck.radius, PUCK_MASS,
                self.hammer2.x, self.hammer2.y, self.hammer2.vel_x, self.hammer2.vel_y, 
                self.hammer2.radius, p2_config.hammer_mass,
                restitution=1.2  # High restitution for hammer (power hit)
            )
        
        # Collision detection: Puck vs Striker 1
        if check_collision_circle(self.puck.x, self.puck.y, self.puck.radius, 
                                 self.striker1.x, self.striker1.y, self.striker1.radius):
            # Separate objects first
            self.puck.x, self.puck.y, self.striker1.x, self.striker1.y = separate_circles(
                self.puck.x, self.puck.y, self.puck.radius,
                self.striker1.x, self.striker1.y, self.striker1.radius
            )
            
            # Resolve collision with momentum transfer
            p1_config = self.config.player1
            self.puck.vel_x, self.puck.vel_y, self.striker1.vel_x, self.striker1.vel_y = resolve_collision(
                self.puck.x, self.puck.y, self.puck.vel_x, self.puck.vel_y, 
                self.puck.radius, PUCK_MASS,
                self.striker1.x, self.striker1.y, self.striker1.vel_x, self.striker1.vel_y, 
                self.striker1.radius, p1_config.striker_mass,
                restitution=0.4  # Low restitution for striker (controlled hit)
            )
        
        # Collision detection: Puck vs Striker 2
        if check_collision_circle(self.puck.x, self.puck.y, self.puck.radius, 
                                 self.striker2.x, self.striker2.y, self.striker2.radius):
            # Separate objects first
            self.puck.x, self.puck.y, self.striker2.x, self.striker2.y = separate_circles(
                self.puck.x, self.puck.y, self.puck.radius,
                self.striker2.x, self.striker2.y, self.striker2.radius
            )
            
            # Resolve collision with momentum transfer
            p2_config = self.config.player2
            self.puck.vel_x, self.puck.vel_y, self.striker2.vel_x, self.striker2.vel_y = resolve_collision(
                self.puck.x, self.puck.y, self.puck.vel_x, self.puck.vel_y, 
                self.puck.radius, PUCK_MASS,
                self.striker2.x, self.striker2.y, self.striker2.vel_x, self.striker2.vel_y, 
                self.striker2.radius, p2_config.striker_mass,
                restitution=0.4  # Low restitution for striker (controlled hit)
            )
    
    def get_time_remaining(self):
        """Get remaining time in seconds"""
        if self.state == GameState.PAUSED:
            # When paused, use the time from when we paused
            elapsed_time = (self.pause_start_time - self.start_time) - self.paused_time
        else:
            # When playing, account for paused time
            elapsed_time = (pygame.time.get_ticks() - self.start_time) - self.paused_time
        remaining_ms = max(0, self.game_duration_ms - elapsed_time)
        return remaining_ms // 1000
    
    def pause_timer(self):
        """Called when game is paused"""
        if self.pause_start_time == 0:  # Only if not already paused
            self.pause_start_time = pygame.time.get_ticks()
    
    def resume_timer(self):
        """Called when game is resumed"""
        if self.pause_start_time > 0:
            # Add the time we were paused to the total paused time
            pause_duration = pygame.time.get_ticks() - self.pause_start_time
            self.paused_time += pause_duration
            self.pause_start_time = 0
    
    def format_time(self, seconds):
        """Format time as MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
    
    def draw(self):
        """Draw all game elements"""
        self.screen.fill(BLACK)  # Clear screen with black background
        
        # Draw goals
        # Left goal (Player 2 scores here)
        pygame.draw.rect(self.screen, GOAL_COLOR, 
                        (GOAL_LEFT_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT))
        # Right goal (Player 1 scores here)
        pygame.draw.rect(self.screen, GOAL_COLOR, 
                        (GOAL_RIGHT_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT))
        
        # Draw center line (like in air hockey)
        pygame.draw.line(self.screen, GRAY, (SCREEN_WIDTH // 2, 0), 
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)
        
        # Draw border (with gaps for goals)
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 4)
        
        # Draw chains first (so they appear behind strikers and hammers)
        self.chain1.draw(self.screen)
        self.chain2.draw(self.screen)
        
        # Draw puck
        self.puck.draw(self.screen)
        
        # Draw strikers
        self.striker1.draw(self.screen)
        self.striker2.draw(self.screen)
        
        # Draw hammers
        self.hammer1.draw(self.screen)
        self.hammer2.draw(self.screen)
        
        # Draw score
        score_font = pygame.font.Font(None, 72)
        score_text = score_font.render(f"{self.player1_score}  -  {self.player2_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(score_text, score_rect)
        
        # Draw timer
        time_remaining = self.get_time_remaining()
        time_text = score_font.render(self.format_time(time_remaining), True, WHITE)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(time_text, time_rect)
        
        # Draw instructions
        font = pygame.font.Font(None, 24)
        if not self.game_over:
            instructions = font.render("P1: Mouse | P2: WASD | SPACE: Reset puck | ESC: Pause", True, GRAY)
            self.screen.blit(instructions, (10, 10))
        else:
            # Draw game over screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.Font(None, 96)
            p1_config = self.config.player1
            p2_config = self.config.player2
            if self.winner == 1:
                winner_text = game_over_font.render("Player 1 Wins!", True, p1_config.striker_color)
            elif self.winner == 2:
                winner_text = game_over_font.render("Player 2 Wins!", True, p2_config.striker_color)
            else:
                winner_text = game_over_font.render("Tie Game!", True, WHITE)
            
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(winner_text, winner_rect)
            
            restart_text = font.render("Press SPACE to restart or ESC to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        # Update display
        pygame.display.flip()
    
    def update_game(self):
        """Update game state (only when playing)"""
        if self.state == GameState.PLAYING and not self.game_over:
            self.update()
    
    def draw_game(self):
        """Draw game (only when playing or paused)"""
        if self.state in (GameState.PLAYING, GameState.PAUSED):
            self.draw()
    
    def get_screen(self):
        """Get the game screen surface"""
        return self.screen

