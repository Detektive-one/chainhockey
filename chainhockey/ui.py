"""
UI components for menus and options screens.
"""

import pygame
from typing import Callable, Optional


class Button:
    """Clickable button with hover states"""
    
    def __init__(self, x, y, width, height, text, font_size=36,
                 color=(100, 100, 100), hover_color=(150, 150, 150),
                 text_color=(255, 255, 255), callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.callback = callback
        self.hovered = False
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False
    
    def draw(self, screen):
        """Draw the button"""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Slider:
    """Draggable slider for numeric values"""
    
    def __init__(self, x, y, width, min_val, max_val, initial_val, step=1.0,
                 label="", callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.value = max(min_val, min(max_val, initial_val))
        self.label = label
        self.callback = callback
        self.dragging = False
        self.font = pygame.font.Font(None, 24)
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value(event.pos[0])
                return True
        return False
    
    def _update_value(self, mouse_x):
        """Update slider value based on mouse position"""
        ratio = max(0, min(1, (mouse_x - self.rect.left) / self.rect.width))
        new_value = self.min_val + ratio * (self.max_val - self.min_val)
        # Snap to step
        new_value = round(new_value / self.step) * self.step
        new_value = max(self.min_val, min(self.max_val, new_value))
        
        if new_value != self.value:
            self.value = new_value
            if self.callback:
                self.callback(self.value)
    
    def draw(self, screen):
        """Draw the slider"""
        # Draw track
        pygame.draw.rect(screen, (100, 100, 100), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)
        
        # Draw handle
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val) if self.max_val != self.min_val else 0
        handle_x = self.rect.left + ratio * self.rect.width
        handle_rect = pygame.Rect(handle_x - 8, self.rect.top - 5, 16, 30)
        pygame.draw.rect(screen, (200, 200, 200), handle_rect)
        pygame.draw.rect(screen, (255, 255, 255), handle_rect, 2)
        
        # Draw label and value
        if self.label:
            label_text = self.font.render(f"{self.label}: {self.value:.2f}", True, (255, 255, 255))
            screen.blit(label_text, (self.rect.x, self.rect.y - 25))


class TextInput:
    """Text input field for direct value entry"""
    
    def __init__(self, x, y, width, height, initial_value="", 
                 numeric=False, min_val=None, max_val=None,
                 callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = str(initial_value)
        self.numeric = numeric
        self.min_val = min_val
        self.max_val = max_val
        self.callback = callback
        self.active = False
        self.font = pygame.font.Font(None, 24)
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self._validate_and_update()
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    return True
                elif event.unicode.isprintable():
                    if not self.numeric or (event.unicode.isdigit() or event.unicode == '.' or event.unicode == '-'):
                        self.text += event.unicode
                        return True
        return False
    
    def _validate_and_update(self):
        """Validate input and update value"""
        if self.numeric:
            try:
                value = float(self.text)
                if self.min_val is not None:
                    value = max(self.min_val, value)
                if self.max_val is not None:
                    value = min(self.max_val, value)
                self.text = str(value)
                if self.callback:
                    self.callback(value)
            except ValueError:
                # Invalid number, revert to last valid value
                pass
    
    def set_value(self, value):
        """Set the text value"""
        self.text = str(value)
    
    def get_value(self):
        """Get the numeric value if numeric, otherwise text"""
        if self.numeric:
            try:
                return float(self.text)
            except ValueError:
                return 0.0
        return self.text
    
    def draw(self, screen):
        """Draw the text input"""
        color = (150, 150, 150) if self.active else (100, 100, 100)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        # Clip text to fit in rect
        text_rect = text_surface.get_rect(left=self.rect.left + 5, centery=self.rect.centery)
        screen.blit(text_surface, text_rect)
        
        # Draw cursor if active
        if self.active:
            cursor_x = text_rect.right + 2
            pygame.draw.line(screen, (255, 255, 255), 
                           (cursor_x, self.rect.top + 5),
                           (cursor_x, self.rect.bottom - 5), 2)


class Label:
    """Text label component"""
    
    def __init__(self, x, y, text, font_size=24, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.color = color
    
    def set_text(self, text):
        """Update label text"""
        self.text = text
    
    def draw(self, screen):
        """Draw the label"""
        text_surface = self.font.render(self.text, True, self.color)
        screen.blit(text_surface, (self.x, self.y))

