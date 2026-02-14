"""
Physics utilities for collision detection and resolution.
"""

import math
from .config import PUCK_MASS, HAMMER_MASS, STRIKER_MASS


def check_collision_circle(x1, y1, r1, x2, y2, r2):
    """Check if two circles are colliding"""
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx * dx + dy * dy)
    return distance < (r1 + r2)


def resolve_collision(obj1_x, obj1_y, obj1_vx, obj1_vy, obj1_r, obj1_mass,
                     obj2_x, obj2_y, obj2_vx, obj2_vy, obj2_r, obj2_mass, restitution=1.0):
    """
    Resolve collision between two circular objects using elastic collision physics.
    Returns new velocities for both objects: (vx1, vy1, vx2, vy2)
    restitution: bounciness factor (1.0 = elastic, <1.0 = inelastic/damped, >1.0 = boosted)
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
    # Impulse magnitude J = -(1+e) * (relative_velocity . normal) / (1/m1 + 1/m2)
    
    j = -(1 + restitution) * dvn
    j /= (1 / obj1_mass + 1 / obj2_mass)
    
    # Apply impulse
    # v1' = v1 + (J/m1) * n
    # v2' = v2 - (J/m2) * n (Remember relative velocity definition affects signs)
    # Here we calculated relative vel as v1 - v2
    
    obj1_vx += (j / obj1_mass) * nx
    obj1_vy += (j / obj1_mass) * ny
    obj2_vx -= (j / obj2_mass) * nx
    obj2_vy -= (j / obj2_mass) * ny
    
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

