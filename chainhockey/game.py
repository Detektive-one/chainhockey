"""
Main game loop and game state management.
"""

import pygame
import sys
from .config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, GRAY,
    GOAL_COLOR, GOAL_LEFT_X, GOAL_RIGHT_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT,
    STRIKER_RADIUS, STRIKER_COLOR, HAMMER_RADIUS, HAMMER_COLOR,
    PUCK_RADIUS, PUCK_COLOR, PUCK_MASS, HAMMER_MASS, STRIKER_MASS
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
        
        # Create game objects
        self.striker = Striker(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                              STRIKER_RADIUS, STRIKER_COLOR)
        self.striker.vel_x = 0
        self.striker.vel_y = 0
        self.striker.prev_x = self.striker.x
        self.striker.prev_y = self.striker.y
        
        # Create chain
        self.chain = Chain(self.striker.x, self.striker.y)
        
        # Create hammer
        hammer_x, hammer_y = self.chain.get_hammer_position()
        self.hammer = Hammer(hammer_x, hammer_y, HAMMER_RADIUS, HAMMER_COLOR)
        
        # Create puck
        self.puck = Puck(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, 
                        PUCK_RADIUS, PUCK_COLOR)
        
        # Score tracking
        self.player1_score = 0  # Right side player
        self.player2_score = 0  # Left side player
        self.goal_delay = 0  # Delay counter after scoring
        
        # Game state
        self.running = True
        self.dt = 1.0  # Delta time for physics
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Reset puck position on spacebar
                    self.puck.reset()
    
    def update(self):
        """Update game state"""
        # Get mouse position and update striker
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate striker velocity before updating position
        self.striker.prev_x = self.striker.x
        self.striker.prev_y = self.striker.y
        self.striker.update_position(mouse_x, mouse_y)
        self.striker.vel_x = self.striker.x - self.striker.prev_x
        self.striker.vel_y = self.striker.y - self.striker.prev_y
        
        # Update chain physics
        self.chain.update(self.dt, self.striker.x, self.striker.y, self.striker.radius)
        
        # Update hammer position based on chain
        hammer_x, hammer_y = self.chain.get_hammer_position()
        self.hammer.update_position(hammer_x, hammer_y)
        
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
    
    def handle_collisions(self):
        """Handle collisions between game objects"""
        # Collision detection: Puck vs Hammer
        if check_collision_circle(self.puck.x, self.puck.y, self.puck.radius, 
                                 self.hammer.x, self.hammer.y, self.hammer.radius):
            # Separate objects first
            self.puck.x, self.puck.y, hammer_x, hammer_y = separate_circles(
                self.puck.x, self.puck.y, self.puck.radius,
                self.hammer.x, self.hammer.y, self.hammer.radius
            )
            
            # Resolve collision with momentum transfer
            self.puck.vel_x, self.puck.vel_y, _, _ = resolve_collision(
                self.puck.x, self.puck.y, self.puck.vel_x, self.puck.vel_y, 
                self.puck.radius, PUCK_MASS,
                self.hammer.x, self.hammer.y, self.hammer.vel_x, self.hammer.vel_y, 
                self.hammer.radius, HAMMER_MASS,
                restitution=1.2  # High restitution for hammer (power hit)
            )
        
        # Collision detection: Puck vs Striker
        if check_collision_circle(self.puck.x, self.puck.y, self.puck.radius, 
                                 self.striker.x, self.striker.y, self.striker.radius):
            # Separate objects first
            self.puck.x, self.puck.y, self.striker.x, self.striker.y = separate_circles(
                self.puck.x, self.puck.y, self.puck.radius,
                self.striker.x, self.striker.y, self.striker.radius
            )
            
            # Resolve collision with momentum transfer
            self.puck.vel_x, self.puck.vel_y, self.striker.vel_x, self.striker.vel_y = resolve_collision(
                self.puck.x, self.puck.y, self.puck.vel_x, self.puck.vel_y, 
                self.puck.radius, PUCK_MASS,
                self.striker.x, self.striker.y, self.striker.vel_x, self.striker.vel_y, 
                self.striker.radius, STRIKER_MASS,
                restitution=0.4  # Low restitution for striker (controlled hit)
            )
    
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
        
        # Draw chain first (so it appears behind striker and hammer)
        self.chain.draw(self.screen)
        
        # Draw puck
        self.puck.draw(self.screen)
        
        # Draw striker
        self.striker.draw(self.screen)
        
        # Draw hammer
        self.hammer.draw(self.screen)
        
        # Draw score
        score_font = pygame.font.Font(None, 72)
        score_text = score_font.render(f"{self.player1_score}  -  {self.player2_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(score_text, score_rect)
        
        # Draw instructions
        font = pygame.font.Font(None, 24)
        instructions = font.render("Move mouse to control | SPACE to reset puck | ESC to quit", True, GRAY)
        self.screen.blit(instructions, (10, 10))
        
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

