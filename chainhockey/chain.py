"""
Chain physics implementation using Verlet integration.
"""

import math
import pygame
from .config import (
    CHAIN_SEGMENTS, SEGMENT_LENGTH, CHAIN_COLOR, CHAIN_THICKNESS,
    DAMPING, GRAVITY, CONSTRAINT_ITERATIONS, CHAIN_SEGMENT_RADIUS,
    SCREEN_WIDTH, SCREEN_HEIGHT, CENTER_LINE_X
)


class ChainSegment:
    """A single point in the chain using Verlet integration"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.old_x = x
        self.old_y = y
        self.pinned = False
    
    def update(self, dt):
        """Update position using Verlet integration"""
        if self.pinned:
            self.old_x = self.x
            self.old_y = self.y
            return
        
        # Calculate velocity from position history
        vel_x = (self.x - self.old_x) * DAMPING
        vel_y = (self.y - self.old_y) * DAMPING
        
        # Store current position
        temp_x = self.x
        temp_y = self.y
        
        # Update position with velocity and gravity
        self.x += vel_x
        self.y += vel_y + GRAVITY * dt * dt
        
        # Store old position
        self.old_x = temp_x
        self.old_y = temp_y
    
    def constrain_to_bounds(self, min_x=None, max_x=None):
        """Keep segment within screen boundaries and optionally restrict to half"""
        if min_x is not None and self.x < min_x:
            self.x = min_x
        elif self.x < 0:
            self.x = 0
            
        if max_x is not None and self.x > max_x:
            self.x = max_x
        elif self.x > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH
        
        if self.y < 0:
            self.y = 0
        elif self.y > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT


class Chain:
    """Physics-based chain connecting striker to hammer"""
    
    def __init__(self, start_x, start_y):
        self.segments = []
        
        # Create chain segments
        for i in range(CHAIN_SEGMENTS + 1):
            x = start_x + i * SEGMENT_LENGTH
            y = start_y
            segment = ChainSegment(x, y)
            self.segments.append(segment)
    
    def update(self, dt, striker_x, striker_y, striker_radius):
        """Update all segments"""
        # Pin first segment to striker
        self.segments[0].x = striker_x
        self.segments[0].y = striker_y
        self.segments[0].pinned = True
        
        # Update all other segments
        for segment in self.segments[1:]:
            segment.update(dt)
            segment.constrain_to_bounds()
        
        # Apply distance constraints multiple times for stability
        for _ in range(CONSTRAINT_ITERATIONS):
            self.apply_constraints()
            # Apply striker collision after each constraint iteration for better stability
            self.apply_striker_collision(striker_x, striker_y, striker_radius)
    
    def apply_constraints(self):
        """Maintain fixed distance between segments"""
        for i in range(len(self.segments) - 1):
            seg1 = self.segments[i]
            seg2 = self.segments[i + 1]
            
            # Calculate distance between segments
            dx = seg2.x - seg1.x
            dy = seg2.y - seg1.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Avoid division by zero
            if distance < 0.01:
                distance = 0.01
            
            # Calculate difference from desired length
            difference = (SEGMENT_LENGTH - distance) / distance
            
            # Move segments to maintain distance
            offset_x = dx * difference * 0.5
            offset_y = dy * difference * 0.5
            
            if not seg1.pinned:
                seg1.x -= offset_x
                seg1.y -= offset_y
            
            if not seg2.pinned:
                seg2.x += offset_x
                seg2.y += offset_y
    
    def apply_striker_collision(self, striker_x, striker_y, striker_radius):
        """Prevent chain segments from passing through the striker"""
        # Check collision for all segments except the first one (which is pinned to striker)
        for i in range(1, len(self.segments)):
            seg = self.segments[i]
            
            # Calculate distance from segment to striker center
            dx = seg.x - striker_x
            dy = seg.y - striker_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Check if segment is colliding with striker
            collision_distance = striker_radius + CHAIN_SEGMENT_RADIUS
            
            if distance < collision_distance and distance > 0.01:
                # Push segment away from striker
                # Normalize direction
                nx = dx / distance
                ny = dy / distance
                
                # Calculate how much to push
                overlap = collision_distance - distance
                
                # Move segment away from striker
                seg.x += nx * overlap
                seg.y += ny * overlap
    
    def get_hammer_position(self):
        """Get position of the last segment (where hammer attaches)"""
        last_seg = self.segments[-1]
        return last_seg.x, last_seg.y
    
    def draw(self, screen):
        """Draw the chain"""
        # Draw chain segments as connected lines
        for i in range(len(self.segments) - 1):
            seg1 = self.segments[i]
            seg2 = self.segments[i + 1]
            pygame.draw.line(screen, CHAIN_COLOR, 
                           (int(seg1.x), int(seg1.y)), 
                           (int(seg2.x), int(seg2.y)), 
                           CHAIN_THICKNESS)
        
        # Draw small circles at each segment for visual effect
        for segment in self.segments:
            pygame.draw.circle(screen, CHAIN_COLOR, 
                             (int(segment.x), int(segment.y)), 3)

