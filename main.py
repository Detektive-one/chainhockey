import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
BLUE = (50, 120, 220)
CYAN = (50, 200, 200)
ORANGE = (255, 140, 50)
GRAY = (100, 100, 100)
YELLOW = (255, 220, 80)

# Striker properties
STRIKER_RADIUS = 20
HAMMER_RADIUS = 35
STRIKER_COLOR = RED
HAMMER_COLOR = ORANGE
STRIKER_MASS = 5.0  # Increased from 1.0 for more weight
HAMMER_MASS = 10.0  # Increased from 2.0 for more weight

# Puck properties
PUCK_RADIUS = 15
PUCK_COLOR = YELLOW
PUCK_MASS = 1  # Increased from 0.8 for more weight
PUCK_FRICTION = 0.985  # Increased friction (was 0.985) - puck slows down faster
PUCK_WALL_BOUNCE = 0.85  # Reduced bounce (was 0.85) - less energy retained

# Chain properties
CHAIN_LENGTH = 30  # Total length of chain
CHAIN_SEGMENTS = 10  # Number of segments in the chain
SEGMENT_LENGTH = 15
CHAIN_COLOR = CYAN
CHAIN_THICKNESS = 3

# Physics
GRAVITY = 0.0  # No gravity for air hockey table
DAMPING = 0.82  # Increased damping (was 0.95) - more air resistance, less floaty
CONSTRAINT_ITERATIONS = 10  # More iterations = more rigid chain
CHAIN_SEGMENT_RADIUS = 2  # Collision radius for chain segments

# Goal properties
GOAL_WIDTH = 20
GOAL_HEIGHT = 200
GOAL_COLOR = (50, 255, 100)  # Green
GOAL_LEFT_X = 0
GOAL_RIGHT_X = SCREEN_WIDTH - GOAL_WIDTH
GOAL_Y = (SCREEN_HEIGHT - GOAL_HEIGHT) // 2  # Centered vertically


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
    
    def constrain_to_bounds(self):
        """Keep segment within screen boundaries"""
        if self.x < 0:
            self.x = 0
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


class Striker:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
    
    def update_position(self, mouse_x, mouse_y):
        """Update striker position to follow mouse, keeping it within bounds"""
        # Keep striker within screen boundaries
        self.x = max(self.radius, min(mouse_x, SCREEN_WIDTH - self.radius))
        self.y = max(self.radius, min(mouse_y, SCREEN_HEIGHT - self.radius))
    
    def draw(self, screen):
        """Draw the striker on the screen"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw a white outline for better visibility
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)


class Hammer:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.prev_x = x
        self.prev_y = y
    
    def update_position(self, x, y):
        """Update hammer position based on chain and calculate velocity"""
        self.prev_x = self.x
        self.prev_y = self.y
        self.x = x
        self.y = y
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
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
    
    def update(self):
        """Update puck position based on velocity. Returns 'left', 'right', or None for goal detection"""
        # Apply friction
        self.vel_x *= PUCK_FRICTION
        self.vel_y *= PUCK_FRICTION
        
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
                self.vel_x = abs(self.vel_x) * PUCK_WALL_BOUNCE
        
        # Right wall (not in goal)
        if self.x + self.radius > SCREEN_WIDTH:
            if not (GOAL_Y < self.y < GOAL_Y + GOAL_HEIGHT):
                self.x = SCREEN_WIDTH - self.radius
                self.vel_x = -abs(self.vel_x) * PUCK_WALL_BOUNCE
        
        # Top and bottom walls
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vel_y = abs(self.vel_y) * PUCK_WALL_BOUNCE
        elif self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.vel_y = -abs(self.vel_y) * PUCK_WALL_BOUNCE
        
        return None
    
    def draw(self, screen):
        """Draw the puck on the screen"""
        # Draw main puck body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw outline
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        # Draw inner circle for depth
        pygame.draw.circle(screen, (255, 240, 150), (int(self.x), int(self.y)), self.radius - 5, 1)


def check_collision_circle(x1, y1, r1, x2, y2, r2):
    """Check if two circles are colliding"""
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx * dx + dy * dy)
    return distance < (r1 + r2)


def resolve_collision(obj1_x, obj1_y, obj1_vx, obj1_vy, obj1_r, obj1_mass,
                     obj2_x, obj2_y, obj2_vx, obj2_vy, obj2_r, obj2_mass):
    """
    Resolve collision between two circular objects using elastic collision physics.
    Returns new velocities for both objects: (vx1, vy1, vx2, vy2)
    """
    # Calculate distance between centers
    dx = obj2_x - obj1_x
    dy = obj2_y - obj1_y
    distance = math.sqrt(dx * dx + dy * dy)
    
    # Avoid division by zero
    if distance < 0.01:
        distance = 0.01
    
    # Normalize collision vector
    nx = dx / distance
    ny = dy / distance
    
    # Relative velocity
    dvx = obj1_vx - obj2_vx
    dvy = obj1_vy - obj2_vy
    
    # Relative velocity in collision normal direction
    dvn = dvx * nx + dvy * ny
    
    # Don't resolve if objects are moving apart
    if dvn < 0:
        return obj1_vx, obj1_vy, obj2_vx, obj2_vy
    
    # Collision impulse
    impulse = (2 * dvn) / (obj1_mass + obj2_mass)
    
    # Update velocities
    obj1_vx -= impulse * obj2_mass * nx
    obj1_vy -= impulse * obj2_mass * ny
    obj2_vx += impulse * obj1_mass * nx
    obj2_vy += impulse * obj1_mass * ny
    
    return obj1_vx, obj1_vy, obj2_vx, obj2_vy


def separate_circles(obj1_x, obj1_y, obj1_r, obj2_x, obj2_y, obj2_r):
    """
    Separate two overlapping circles.
    Returns new positions: (x1, y1, x2, y2)
    """
    dx = obj2_x - obj1_x
    dy = obj2_y - obj1_y
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance < 0.01:
        distance = 0.01
    
    # Calculate overlap
    overlap = (obj1_r + obj2_r) - distance
    
    if overlap > 0:
        # Normalize
        nx = dx / distance
        ny = dy / distance
        
        # Move objects apart
        obj1_x -= nx * overlap * 0.5
        obj1_y -= ny * overlap * 0.5
        obj2_x += nx * overlap * 0.5
        obj2_y += ny * overlap * 0.5
    
    return obj1_x, obj1_y, obj2_x, obj2_y


def reset_puck(puck):
    """Reset puck to center position with no velocity"""
    puck.x = SCREEN_WIDTH // 2
    puck.y = SCREEN_HEIGHT // 2
    puck.vel_x = 0
    puck.vel_y = 0


def main():
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chain Hockey - Meteor Hammer")
    
    # Clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Create striker at center of screen
    striker = Striker(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, STRIKER_RADIUS, STRIKER_COLOR)
    striker.vel_x = 0
    striker.vel_y = 0
    striker.prev_x = striker.x
    striker.prev_y = striker.y
    
    # Create chain
    chain = Chain(striker.x, striker.y)
    
    # Create hammer
    hammer_x, hammer_y = chain.get_hammer_position()
    hammer = Hammer(hammer_x, hammer_y, HAMMER_RADIUS, HAMMER_COLOR)
    
    # Create puck at center
    puck = Puck(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, PUCK_RADIUS, PUCK_COLOR)
    
    # Score tracking
    player1_score = 0  # Right side player
    player2_score = 0  # Left side player
    goal_delay = 0  # Delay counter after scoring
    
    # Main game loop
    running = True
    dt = 1.0  # Delta time for physics
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Reset puck position on spacebar
                    puck.x = SCREEN_WIDTH // 2
                    puck.y = SCREEN_HEIGHT // 2
                    puck.vel_x = 0
                    puck.vel_y = 0
        
        # Get mouse position and update striker
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate striker velocity before updating position
        striker.prev_x = striker.x
        striker.prev_y = striker.y
        striker.update_position(mouse_x, mouse_y)
        striker.vel_x = striker.x - striker.prev_x
        striker.vel_y = striker.y - striker.prev_y
        
        # Update chain physics
        chain.update(dt, striker.x, striker.y, striker.radius)
        
        # Update hammer position based on chain
        hammer_x, hammer_y = chain.get_hammer_position()
        hammer.update_position(hammer_x, hammer_y)
        
        # Update puck physics and check for goals
        if goal_delay > 0:
            goal_delay -= 1
        else:
            goal_result = puck.update()
            
            # Check if a goal was scored
            if goal_result == 'left':
                player2_score += 1
                reset_puck(puck)
                goal_delay = 60  # 1 second delay at 60 FPS
            elif goal_result == 'right':
                player1_score += 1
                reset_puck(puck)
                goal_delay = 60  # 1 second delay at 60 FPS
        
        # Collision detection: Puck vs Hammer
        if check_collision_circle(puck.x, puck.y, puck.radius, 
                                 hammer.x, hammer.y, hammer.radius):
            # Separate objects first
            puck.x, puck.y, hammer_x, hammer_y = separate_circles(
                puck.x, puck.y, puck.radius,
                hammer.x, hammer.y, hammer.radius
            )
            
            # Resolve collision with momentum transfer
            puck.vel_x, puck.vel_y, _, _ = resolve_collision(
                puck.x, puck.y, puck.vel_x, puck.vel_y, puck.radius, PUCK_MASS,
                hammer.x, hammer.y, hammer.vel_x, hammer.vel_y, hammer.radius, HAMMER_MASS
            )
        
        # Collision detection: Puck vs Striker
        if check_collision_circle(puck.x, puck.y, puck.radius, 
                                 striker.x, striker.y, striker.radius):
            # Separate objects first
            puck.x, puck.y, striker.x, striker.y = separate_circles(
                puck.x, puck.y, puck.radius,
                striker.x, striker.y, striker.radius
            )
            
            # Resolve collision with momentum transfer
            puck.vel_x, puck.vel_y, striker.vel_x, striker.vel_y = resolve_collision(
                puck.x, puck.y, puck.vel_x, puck.vel_y, puck.radius, PUCK_MASS,
                striker.x, striker.y, striker.vel_x, striker.vel_y, striker.radius, STRIKER_MASS
            )
        
        # Drawing
        screen.fill(BLACK)  # Clear screen with black background
        
        # Draw goals
        # Left goal (Player 2 scores here)
        pygame.draw.rect(screen, GOAL_COLOR, (GOAL_LEFT_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT))
        # Right goal (Player 1 scores here)
        pygame.draw.rect(screen, GOAL_COLOR, (GOAL_RIGHT_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT))
        
        # Draw center line (like in air hockey)
        pygame.draw.line(screen, GRAY, (SCREEN_WIDTH // 2, 0), 
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)
        
        # Draw border (with gaps for goals)
        pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 4)
        
        # Draw chain first (so it appears behind striker and hammer)
        chain.draw(screen)
        
        # Draw puck
        puck.draw(screen)
        
        # Draw striker
        striker.draw(screen)
        
        # Draw hammer
        hammer.draw(screen)
        
        # Draw score
        score_font = pygame.font.Font(None, 72)
        score_text = score_font.render(f"{player1_score}  -  {player2_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(score_text, score_rect)
        
        # Draw instructions
        font = pygame.font.Font(None, 24)
        instructions = font.render("Move mouse to control | SPACE to reset puck | ESC to quit", True, GRAY)
        screen.blit(instructions, (10, 10))
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)
    
    # Quit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
