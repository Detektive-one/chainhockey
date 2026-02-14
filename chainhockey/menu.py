"""
Menu screens for the game.
"""

import pygame
from enum import Enum
from typing import Optional, Callable
from .ui import Button, Slider, TextInput, Label
from .config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GRAY
from .config_manager import ConfigManager, GameConfig, PlayerConfig


class MenuState(Enum):
    """Menu state transitions"""
    START = "start"
    PAUSE = "pause"
    OPTIONS = "options"
    GAME = "game"
    EXIT = "exit"


class StartMenu:
    """Main start menu"""
    
    def __init__(self, screen, on_start: Callable, on_options: Callable, on_exit: Callable):
        self.screen = screen
        self.on_start = on_start
        self.on_options = on_options
        self.on_exit = on_exit
        
        center_x = SCREEN_WIDTH // 2
        button_width = 300
        button_height = 60
        button_y_start = SCREEN_HEIGHT // 2 - 50
        
        self.start_button = Button(
            center_x - button_width // 2, button_y_start,
            button_width, button_height, "Start Game",
            callback=lambda: self.on_start()
        )
        
        self.options_button = Button(
            center_x - button_width // 2, button_y_start + 80,
            button_width, button_height, "Options",
            callback=lambda: self.on_options()
        )
        
        self.exit_button = Button(
            center_x - button_width // 2, button_y_start + 160,
            button_width, button_height, "Exit",
            callback=lambda: self.on_exit()
        )
        
        self.title_font = pygame.font.Font(None, 96)
    
    def handle_event(self, event):
        """Handle events"""
        self.start_button.handle_event(event)
        self.options_button.handle_event(event)
        self.exit_button.handle_event(event)
    
    def draw(self):
        """Draw the menu"""
        self.screen.fill(BLACK)
        
        # Draw title
        title_text = self.title_font.render("Chain Hockey", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Draw buttons
        self.start_button.draw(self.screen)
        self.options_button.draw(self.screen)
        self.exit_button.draw(self.screen)


class PauseMenu:
    """Pause menu"""
    
    def __init__(self, screen, on_resume: Callable, on_options: Callable, on_main_menu: Callable):
        self.screen = screen
        self.on_resume = on_resume
        self.on_options = on_options
        self.on_main_menu = on_main_menu
        
        center_x = SCREEN_WIDTH // 2
        button_width = 300
        button_height = 60
        button_y_start = SCREEN_HEIGHT // 2 - 50
        
        self.resume_button = Button(
            center_x - button_width // 2, button_y_start,
            button_width, button_height, "Resume",
            callback=lambda: self.on_resume()
        )
        
        self.options_button = Button(
            center_x - button_width // 2, button_y_start + 80,
            button_width, button_height, "Options",
            callback=lambda: self.on_options()
        )
        
        self.main_menu_button = Button(
            center_x - button_width // 2, button_y_start + 160,
            button_width, button_height, "Main Menu",
            callback=lambda: self.on_main_menu()
        )
        
        self.title_font = pygame.font.Font(None, 72)
    
    def handle_event(self, event):
        """Handle events"""
        self.resume_button.handle_event(event)
        self.options_button.handle_event(event)
        self.main_menu_button.handle_event(event)
    
    def draw(self, game_screen):
        """Draw pause menu overlay"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self.title_font.render("PAUSED", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Draw buttons
        self.resume_button.draw(self.screen)
        self.options_button.draw(self.screen)
        self.main_menu_button.draw(self.screen)


class OptionsMenu:
    """Options menu with configuration controls"""
    
    def __init__(self, screen, config_manager: ConfigManager, on_back: Callable):
        self.screen = screen
        self.config_manager = config_manager
        self.on_back = on_back
        self.config = config_manager.get_config()
        
        # Scroll offset for scrollable menu
        self.scroll_offset = 0
        self.scroll_speed = 30
        
        # UI elements
        self.buttons = []
        self.sliders = []
        self.text_inputs = []
        self.labels = []
        
        self._create_ui()
    
    def _create_ui(self):
        """Create all UI elements"""
        # Back button
        back_button = Button(
            50, SCREEN_HEIGHT - 70, 200, 50, "Back",
            callback=lambda: self.on_back()
        )
        self.buttons.append(back_button)
        
        # Save/Load/Reset buttons
        save_button = Button(
            SCREEN_WIDTH - 250, SCREEN_HEIGHT - 70, 200, 50, "Save Config",
            callback=lambda: self._save_config()
        )
        self.buttons.append(save_button)
        
        load_button = Button(
            SCREEN_WIDTH - 250, SCREEN_HEIGHT - 130, 200, 50, "Load Config",
            callback=lambda: self._load_config()
        )
        self.buttons.append(load_button)
        
        reset_button = Button(
            SCREEN_WIDTH - 250, SCREEN_HEIGHT - 190, 200, 50, "Reset Defaults",
            callback=lambda: self._reset_defaults()
        )
        self.buttons.append(reset_button)
        
        # Title
        title = Label(SCREEN_WIDTH // 2 - 150, 20, "OPTIONS", 72, WHITE)
        self.labels.append(title)
        
        # Player 1 section
        self._create_player_section(1, 50, 100)
        
        # Player 2 section
        self._create_player_section(2, SCREEN_WIDTH // 2 + 50, 100)
        
        # Global physics section
        self._create_global_section()
    
    def _create_player_section(self, player_num, x, y):
        """Create UI for a player's configuration"""
        player_config = self.config.player1 if player_num == 1 else self.config.player2
        player_name = f"Player {player_num}"
        
        # Apply scroll offset
        y = y - self.scroll_offset
        
        # Player title
        title = Label(x, y, player_name, 36, WHITE)
        self.labels.append(title)
        
        y_offset = y + 50
        
        # Striker section
        striker_label = Label(x, y_offset, "Striker", 28, GRAY)
        self.labels.append(striker_label)
        y_offset += 35
        
        # Striker radius
        self._add_slider(x, y_offset, 200, 5, 50, player_config.striker_radius, 1.0,
                        "Radius", lambda v: setattr(player_config, 'striker_radius', v))
        y_offset += 50
        
        # Striker mass
        self._add_slider(x, y_offset, 200, 1, 20, player_config.striker_mass, 0.5,
                        "Mass", lambda v: setattr(player_config, 'striker_mass', v))
        y_offset += 50
        
        # Striker speed
        self._add_slider(x, y_offset, 200, 1, 15, player_config.striker_speed, 0.5,
                        "Speed", lambda v: setattr(player_config, 'striker_speed', v))
        y_offset += 50
        
        # Striker color RGB
        color_label = Label(x, y_offset - self.scroll_offset, "Color (RGB):", 24, WHITE)
        self.labels.append(color_label)
        y_offset += 30
        
        self._add_color_sliders(x, y_offset, player_config, 'striker_color')
        y_offset += 100
        
        # Chain section
        chain_label = Label(x, y_offset - self.scroll_offset, "Chain", 28, GRAY)
        self.labels.append(chain_label)
        y_offset += 35
        
        # Chain segments
        self._add_slider(x, y_offset, 200, 3, 30, player_config.chain_segments, 1,
                        "Segments", lambda v: setattr(player_config, 'chain_segments', int(v)))
        y_offset += 50
        
        # Segment length
        self._add_slider(x, y_offset, 200, 5, 30, player_config.segment_length, 1.0,
                        "Length", lambda v: setattr(player_config, 'segment_length', v))
        y_offset += 50
        
        # Chain thickness
        self._add_slider(x, y_offset, 200, 1, 10, player_config.chain_thickness, 1,
                        "Thickness", lambda v: setattr(player_config, 'chain_thickness', int(v)))
        y_offset += 50
        
        # Chain damping
        self._add_slider(x, y_offset, 200, 0.5, 1.0, player_config.chain_damping, 0.01,
                        "Damping", lambda v: setattr(player_config, 'chain_damping', v))
        y_offset += 50
        
        # Chain color RGB
        color_label = Label(x, y_offset - self.scroll_offset, "Color (RGB):", 24, WHITE)
        self.labels.append(color_label)
        y_offset += 30
        
        self._add_color_sliders(x, y_offset, player_config, 'chain_color')
        y_offset += 100
        
        # Hammer section
        hammer_label = Label(x, y_offset - self.scroll_offset, "Hammer", 28, GRAY)
        self.labels.append(hammer_label)
        y_offset += 35
        
        # Hammer radius
        self._add_slider(x, y_offset, 200, 10, 60, player_config.hammer_radius, 1.0,
                        "Radius", lambda v: setattr(player_config, 'hammer_radius', v))
        y_offset += 50
        
        # Hammer mass
        self._add_slider(x, y_offset, 200, 1, 30, player_config.hammer_mass, 0.5,
                        "Mass", lambda v: setattr(player_config, 'hammer_mass', v))
        y_offset += 50
        
        # Hammer color RGB
        color_label = Label(x, y_offset - self.scroll_offset, "Color (RGB):", 24, WHITE)
        self.labels.append(color_label)
        y_offset += 30
        
        self._add_color_sliders(x, y_offset, player_config, 'hammer_color')
    
    def _create_global_section(self):
        """Create UI for global physics settings"""
        x = SCREEN_WIDTH // 2 - 150
        y = 500 - self.scroll_offset
        
        global_label = Label(x, y, "Global Physics", 28, GRAY)
        self.labels.append(global_label)
        y += 35
        
        # Gravity
        self._add_slider(x, y, 300, -1.0, 1.0, self.config.gravity, 0.01,
                        "Gravity", lambda v: setattr(self.config, 'gravity', v))
        y += 50
        
        # Constraint iterations
        self._add_slider(x, y, 300, 5, 30, self.config.constraint_iterations, 1,
                        "Constraint Iterations", lambda v: setattr(self.config, 'constraint_iterations', int(v)))
        y += 50
        
        # Puck friction
        self._add_slider(x, y, 300, 0.9, 1.0, self.config.puck_friction, 0.001,
                        "Puck Friction", lambda v: setattr(self.config, 'puck_friction', v))
        y += 50
        
        # Puck wall bounce
        self._add_slider(x, y, 300, 0.5, 1.0, self.config.puck_wall_bounce, 0.01,
                        "Puck Wall Bounce", lambda v: setattr(self.config, 'puck_wall_bounce', v))
        y += 50
        
        # Game duration
        self._add_slider(x, y, 300, 60, 600, self.config.game_duration_seconds, 30,
                        "Game Duration (sec)", lambda v: setattr(self.config, 'game_duration_seconds', int(v)))
        y += 50
        
        # Max goals
        self._add_slider(x, y, 300, 1, 20, self.config.max_goals, 1,
                        "Max Goals", lambda v: setattr(self.config, 'max_goals', int(v)))
    
    def _add_slider(self, x, y, width, min_val, max_val, initial_val, step, label, callback):
        """Add a slider to the UI"""
        # Apply scroll offset
        y = y - self.scroll_offset
        slider = Slider(x, y, width, min_val, max_val, initial_val, step, label, callback)
        self.sliders.append(slider)
    
    def _add_color_sliders(self, x, y, player_config, color_attr):
        """Add RGB color sliders"""
        current_color = getattr(player_config, color_attr)
        
        # Apply scroll offset
        y = y - self.scroll_offset
        
        # R slider
        r_slider = Slider(x, y, 200, 0, 255, current_color[0], 1, "R",
                         lambda v: setattr(player_config, color_attr, 
                                          (int(v), current_color[1], current_color[2])))
        self.sliders.append(r_slider)
        
        # G slider
        g_slider = Slider(x, y + 30, 200, 0, 255, current_color[1], 1, "G",
                         lambda v: setattr(player_config, color_attr,
                                          (current_color[0], int(v), current_color[2])))
        self.sliders.append(g_slider)
        
        # B slider
        b_slider = Slider(x, y + 60, 200, 0, 255, current_color[2], 1, "B",
                         lambda v: setattr(player_config, color_attr,
                                          (current_color[0], current_color[1], int(v))))
        self.sliders.append(b_slider)
    
    def _save_config(self):
        """Save current configuration"""
        self.config_manager.set_config(self.config)
        self.config_manager.save()
    
    def _load_config(self):
        """Load configuration from file"""
        self.config_manager.load()
        self.config = self.config_manager.get_config()
        # Recreate UI with new config values
        self.buttons.clear()
        self.sliders.clear()
        self.text_inputs.clear()
        self.labels.clear()
        self._create_ui()
    
    def _reset_defaults(self):
        """Reset to default configuration"""
        self.config = GameConfig.default()
        self.config_manager.set_config(self.config)
        # Recreate UI with default values
        self.buttons.clear()
        self.sliders.clear()
        self.text_inputs.clear()
        self.labels.clear()
        self._create_ui()
    
    def handle_event(self, event):
        """Handle events"""
        # Handle scrolling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                # Recreate UI with new scroll offset
                self.buttons.clear()
                self.sliders.clear()
                self.text_inputs.clear()
                self.labels.clear()
                self._create_ui()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.scroll_offset += self.scroll_speed
                # Recreate UI with new scroll offset
                self.buttons.clear()
                self.sliders.clear()
                self.text_inputs.clear()
                self.labels.clear()
                self._create_ui()
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, self.scroll_offset - event.y * self.scroll_speed)
            # Recreate UI with new scroll offset
            self.buttons.clear()
            self.sliders.clear()
            self.text_inputs.clear()
            self.labels.clear()
            self._create_ui()
        
        for button in self.buttons:
            button.handle_event(event)
        for slider in self.sliders:
            slider.handle_event(event)
        for text_input in self.text_inputs:
            text_input.handle_event(event)
    
    def draw(self):
        """Draw the options menu"""
        self.screen.fill(BLACK)
        
        # Draw scroll instructions
        font = pygame.font.Font(None, 24)
        scroll_text = font.render("Use Mouse Wheel, UP/DOWN, or W/S to scroll", True, GRAY)
        self.screen.blit(scroll_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 30))
        
        # Draw labels (only if visible on screen)
        for label in self.labels:
            if 0 <= label.y <= SCREEN_HEIGHT:
                label.draw(self.screen)
        
        # Draw buttons (always visible at bottom)
        for button in self.buttons:
            button.draw(self.screen)
        
        # Draw sliders (only if visible on screen)
        for slider in self.sliders:
            if 0 <= slider.rect.y <= SCREEN_HEIGHT:
                slider.draw(self.screen)
        
        # Draw text inputs (only if visible on screen)
        for text_input in self.text_inputs:
            if 0 <= text_input.rect.y <= SCREEN_HEIGHT:
                text_input.draw(self.screen)

