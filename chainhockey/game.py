"""
Main game loop and game state management.
"""

import pygame
import sys
from .config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, GRAY,
    GOAL_COLOR, GOAL_LEFT_X, GOAL_RIGHT_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT,
    STRIKER_RADIUS, STRIKER_COLOR, HAMMER_RADIUS, HAMMER_COLOR,
    PUCK_RADIUS, PUCK_COLOR, PUCK_MASS, HAMMER_MASS, STRIKER_MASS,
    PLAYER1_COLOR, PLAYER2_COLOR, PLAYER1_SPAWN_X, PLAYER2_SPAWN_X,
    PLAYER_SPAWN_Y, CENTER_LINE_X, GAME_DURATION_SECONDS, MAX_GOALS,
    CHAIN1_COLOR, CHAIN2_COLOR
)
from .chain import Chain
from .game_objects import Striker, Hammer, Puck
from .physics import check_collision_circle, resolve_collision, separate_circles


class ChainHockeyGame:
    """Main game class managing the game loop and state"""
    
    def __init__(self):
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chain Hockey - Meteor Hammer")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Player boundaries
        # Player 1 (right side) can move from center to right edge
        player1_min_x = CENTER_LINE_X + STRIKER_RADIUS
        player1_max_x = SCREEN_WIDTH - STRIKER_RADIUS
        # Player 2 (left side) can move from left edge to center
        player2_min_x = STRIKER_RADIUS
        player2_max_x = CENTER_LINE_X - STRIKER_RADIUS
        
        # Create Player 1 (right side, mouse controlled)
        self.striker1 = Striker(PLAYER1_SPAWN_X, PLAYER_SPAWN_Y, 
                               STRIKER_RADIUS, PLAYER1_COLOR,
                               player1_min_x, player1_max_x, is_player1=True)
        self.striker1.vel_x = 0
        self.striker1.vel_y = 0
        self.striker1.prev_x = self.striker1.x
        self.striker1.prev_y = self.striker1.y
        
        # Create Player 2 (left side, WASD controlled)
        self.striker2 = Striker(PLAYER2_SPAWN_X, PLAYER_SPAWN_Y,
                               STRIKER_RADIUS, PLAYER2_COLOR,
                               player2_min_x, player2_max_x, is_player1=False)
        self.striker2.vel_x = 0
        self.striker2.vel_y = 0
        self.striker2.prev_x = self.striker2.x
        self.striker2.prev_y = self.striker2.y
        
        # Create chains with different colors
        self.chain1 = Chain(self.striker1.x, self.striker1.y, CHAIN1_COLOR)
        self.chain2 = Chain(self.striker2.x, self.striker2.y, CHAIN2_COLOR)
        
        # Create hammers
        hammer1_x, hammer1_y = self.chain1.get_hammer_position()
        self.hammer1 = Hammer(hammer1_x, hammer1_y, HAMMER_RADIUS, HAMMER_COLOR,
                              player1_min_x, player1_max_x)
        hammer2_x, hammer2_y = self.chain2.get_hammer_position()
        self.hammer2 = Hammer(hammer2_x, hammer2_y, HAMMER_RADIUS, HAMMER_COLOR,
                              player2_min_x, player2_max_x)
        
        # Create puck
        self.puck = Puck(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                        PUCK_RADIUS, PUCK_COLOR)
        
        # Score tracking
        self.player1_score = 0  # Right side player
        self.player2_score = 0  # Left side player
        self.goal_delay = 0  # Delay counter after scoring
        
        # Game state
        self.running = True
        self.dt = 1.0  # Delta time for physics
        self.game_over = False
        self.winner = None
        
        # Timer
        self.start_time = pygame.time.get_ticks()
        self.game_duration_ms = GAME_DURATION_SECONDS * 1000
        
        # Store boundaries for chain updates
        self.player1_min_x = player1_min_x
        self.player1_max_x = player1_max_x
        self.player2_min_x = player2_min_x
        self.player2_max_x = player2_max_x
    
    def reset_game(self):
        """Reset game state without reinitializing display"""
        # Reset strikers to spawn positions
        self.striker1.x = PLAYER1_SPAWN_X
        self.striker1.y = PLAYER_SPAWN_Y
        self.striker1.vel_x = 0
        self.striker1.vel_y = 0
        self.striker1.prev_x = self.striker1.x
        self.striker1.prev_y = self.striker1.y
        
        self.striker2.x = PLAYER2_SPAWN_X
        self.striker2.y = PLAYER_SPAWN_Y
        self.striker2.vel_x = 0
        self.striker2.vel_y = 0
        self.striker2.prev_x = self.striker2.x
        self.striker2.prev_y = self.striker2.y
        
        # Reset chains
        self.chain1 = Chain(self.striker1.x, self.striker1.y, CHAIN1_COLOR)
        self.chain2 = Chain(self.striker2.x, self.striker2.y, CHAIN2_COLOR)
        
        # Reset hammers
        hammer1_x, hammer1_y = self.chain1.get_hammer_position()
        self.hammer1 = Hammer(hammer1_x, hammer1_y, HAMMER_RADIUS, HAMMER_COLOR,
                              self.player1_min_x, self.player1_max_x)
        hammer2_x, hammer2_y = self.chain2.get_hammer_position()
        self.hammer2 = Hammer(hammer2_x, hammer2_y, HAMMER_RADIUS, HAMMER_COLOR,
                              self.player2_min_x, self.player2_max_x)
        
        # Reset puck
        self.puck.reset()
        
        # Reset scores and game state
        self.player1_score = 0
        self.player2_score = 0
        self.goal_delay = 0
        self.game_over = False
        self.winner = None
        self.start_time = pygame.time.get_ticks()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        # Restart game
                        self.reset_game()
                    else:
                        # Reset puck position on spacebar
                        self.puck.reset()
    
    def check_win_condition(self):
        """Check if game should end (5 minutes or 10 goals)"""
        if self.game_over:
            return
        
        # Check goal limit
        if self.player1_score >= MAX_GOALS:
            self.game_over = True
            self.winner = 1
            return
        if self.player2_score >= MAX_GOALS:
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
        self.chain1.update(self.dt, self.striker1.x, self.striker1.y, 
                          self.striker1.radius, self.player1_min_x, self.player1_max_x)
        self.chain2.update(self.dt, self.striker2.x, self.striker2.y,
                          self.striker2.radius, self.player2_min_x, self.player2_max_x)
        
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
            self.puck.vel_x, self.puck.vel_y, _, _ = resolve_collision(
                self.puck.x, self.puck.y, self.puck.vel_x, self.puck.vel_y, 
                self.puck.radius, PUCK_MASS,
                self.hammer1.x, self.hammer1.y, self.hammer1.vel_x, self.hammer1.vel_y, 
                self.hammer1.radius, HAMMER_MASS,
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
            self.puck.vel_x, self.puck.vel_y, _, _ = resolve_collision(
                self.puck.x, self.puck.y, self.puck.vel_x, self.puck.vel_y, 
                self.puck.radius, PUCK_MASS,
                self.hammer2.x, self.hammer2.y, self.hammer2.vel_x, self.hammer2.vel_y, 
                self.hammer2.radius, HAMMER_MASS,
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
            self.puck.vel_x, self.puck.vel_y, self.striker1.vel_x, self.striker1.vel_y = resolve_collision(
                self.puck.x, self.puck.y, self.puck.vel_x, self.puck.vel_y, 
                self.puck.radius, PUCK_MASS,
                self.striker1.x, self.striker1.y, self.striker1.vel_x, self.striker1.vel_y, 
                self.striker1.radius, STRIKER_MASS,
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
            self.puck.vel_x, self.puck.vel_y, self.striker2.vel_x, self.striker2.vel_y = resolve_collision(
                self.puck.x, self.puck.y, self.puck.vel_x, self.puck.vel_y, 
                self.puck.radius, PUCK_MASS,
                self.striker2.x, self.striker2.y, self.striker2.vel_x, self.striker2.vel_y, 
                self.striker2.radius, STRIKER_MASS,
                restitution=0.4  # Low restitution for striker (controlled hit)
            )
    
    def get_time_remaining(self):
        """Get remaining time in seconds"""
        elapsed_time = pygame.time.get_ticks() - self.start_time
        remaining_ms = max(0, self.game_duration_ms - elapsed_time)
        return remaining_ms // 1000
    
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
            instructions = font.render("P1: Mouse | P2: WASD | SPACE: Reset puck | ESC: Quit", True, GRAY)
            self.screen.blit(instructions, (10, 10))
        else:
            # Draw game over screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.Font(None, 96)
            if self.winner == 1:
                winner_text = game_over_font.render("Player 1 Wins!", True, PLAYER1_COLOR)
            elif self.winner == 2:
                winner_text = game_over_font.render("Player 2 Wins!", True, PLAYER2_COLOR)
            else:
                winner_text = game_over_font.render("Tie Game!", True, WHITE)
            
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(winner_text, winner_rect)
            
            restart_text = font.render("Press SPACE to restart or ESC to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            # Control frame rate
            self.clock.tick(FPS)
        
        # Quit
        pygame.quit()
        sys.exit()

