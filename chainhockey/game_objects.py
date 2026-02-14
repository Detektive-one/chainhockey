"""
Game objects: Striker, Hammer, and Puck.
"""

import pygame
from .config import (
    STRIKER_RADIUS, STRIKER_COLOR, HAMMER_RADIUS, HAMMER_COLOR,
    PUCK_RADIUS, PUCK_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT,
    GOAL_WIDTH, GOAL_HEIGHT, GOAL_Y, PUCK_FRICTION, PUCK_WALL_BOUNCE,
    WHITE, STRIKER_SPEED, CENTER_LINE_X
)
from typing import Optional


class Striker:
    """Player-controlled striker that can be controlled by mouse or keyboard"""
    
    def __init__(self, x, y, radius=STRIKER_RADIUS, color=STRIKER_COLOR, 
                 min_x=None, max_x=None, is_player1=True, speed: Optional[float] = None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.prev_x = x
        self.prev_y = y
        self.min_x = min_x if min_x is not None else self.radius
        self.max_x = max_x if max_x is not None else SCREEN_WIDTH - self.radius
        self.is_player1 = is_player1
        self.speed = speed if speed is not None else STRIKER_SPEED
    
    def update_position_mouse(self, mouse_x, mouse_y):
        """Update striker position to follow mouse, keeping it within bounds"""
        # Keep striker within screen boundaries and player's half
        self.x = max(self.min_x, min(mouse_x, self.max_x))
        self.y = max(self.radius, min(mouse_y, SCREEN_HEIGHT - self.radius))
    
    def update_position_keyboard(self, keys):
        """Update striker position based on keyboard input (WASD)"""
        dx = 0
        dy = 0
        
        if keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_s]:
            dy += self.speed
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed
        
        # Update position
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Constrain to boundaries and player's half
        self.x = max(self.min_x, min(new_x, self.max_x))
        self.y = max(self.radius, min(new_y, SCREEN_HEIGHT - self.radius))
    
    def draw(self, screen):
        """Draw the striker on the screen"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw a white outline for better visibility
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)


class Hammer:
    """Hammer attached to the end of the chain"""
    
    def __init__(self, x, y, radius=HAMMER_RADIUS, color=HAMMER_COLOR, min_x=None, max_x=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.prev_x = x
        self.prev_y = y
        self.min_x = min_x if min_x is not None else self.radius
        self.max_x = max_x if max_x is not None else SCREEN_WIDTH - self.radius
    
    def update_position(self, x, y):
        """Update hammer position based on chain and calculate velocity"""
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Constrain hammer to player's half
        self.x = max(self.min_x, min(x, self.max_x))
        self.y = max(self.radius, min(y, SCREEN_HEIGHT - self.radius))
        
        # Calculate velocity from position change
        self.vel_x = self.x - self.prev_x
        self.vel_y = self.y - self.prev_y
    
    def draw(self, screen):
        """Draw the hammer on the screen"""
        # Draw main hammer body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw darker outline
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 3)
        # Draw inner detail circle
        pygame.draw.circle(screen, (255, 180, 100), (int(self.x), int(self.y)), self.radius - 10, 2)


class Puck:
    """The puck that players try to score with"""
    
    def __init__(self, x, y, radius=PUCK_RADIUS, color=PUCK_COLOR,
                 friction: Optional[float] = None, wall_bounce: Optional[float] = None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.friction = friction if friction is not None else PUCK_FRICTION
        self.wall_bounce = wall_bounce if wall_bounce is not None else PUCK_WALL_BOUNCE
    
    def update(self):
        """Update puck position based on velocity. Returns 'left', 'right', or None for goal detection"""
        # Apply friction
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Check for goals first
        # Left goal (player 2 scores)
        if self.x - self.radius < GOAL_WIDTH and GOAL_Y < self.y < GOAL_Y + GOAL_HEIGHT:
            return 'left'
        
        # Right goal (player 1 scores)
        if self.x + self.radius > SCREEN_WIDTH - GOAL_WIDTH and GOAL_Y < self.y < GOAL_Y + GOAL_HEIGHT:
            return 'right'
        
        # Wall collision detection and bouncing (excluding goal areas)
        # Left wall (not in goal)
        if self.x - self.radius < 0:
            if not (GOAL_Y < self.y < GOAL_Y + GOAL_HEIGHT):
                self.x = self.radius
                self.vel_x = abs(self.vel_x) * self.wall_bounce
        
        # Right wall (not in goal)
        if self.x + self.radius > SCREEN_WIDTH:
            if not (GOAL_Y < self.y < GOAL_Y + GOAL_HEIGHT):
                self.x = SCREEN_WIDTH - self.radius
                self.vel_x = -abs(self.vel_x) * self.wall_bounce
        
        # Top and bottom walls
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vel_y = abs(self.vel_y) * self.wall_bounce
        elif self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.vel_y = -abs(self.vel_y) * self.wall_bounce
        
        return None
    
    def reset(self):
        """Reset puck to center position with no velocity"""
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.vel_x = 0
        self.vel_y = 0
    
    def draw(self, screen):
        """Draw the puck on the screen"""
        # Draw main puck body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw outline
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        # Draw inner circle for depth
        pygame.draw.circle(screen, (255, 240, 150), (int(self.x), int(self.y)), self.radius - 5, 1)

