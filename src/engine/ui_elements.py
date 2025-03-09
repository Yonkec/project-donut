import pygame
from typing import List, Dict, Callable, Tuple

class UIElement:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        
    def handle_event(self, event) -> bool:
        """Return True if event was consumed"""
        return False
        
    def update(self):
        pass
        
    def render(self, surface):
        pass

class Button(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Callable, color: Tuple[int, int, int] = (100, 100, 200)):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.disabled_color = (100, 100, 100)
        self.is_hovered = False
        self.ui_manager = None
        
    def handle_event(self, event) -> bool:
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.ui_manager:
                    self.ui_manager.play_drop_sound()
                self.callback()
                return True
                
        return False
        
    def render(self, surface):
        if not self.visible:
            return
            
        color = self.disabled_color if not self.enabled else (self.hover_color if self.is_hovered else self.color)
        pygame.draw.rect(surface, color, self.rect)
        
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class Label(UIElement):
    def __init__(self, x: int, y: int, text: str, color: Tuple[int, int, int] = (255, 255, 255),
                 font_size: int = 24):
        super().__init__(x, y, 0, 0)
        self._text = text
        self.color = color
        self.font_size = font_size
        self.font = pygame.font.SysFont(None, font_size)
        self._update_dimensions()
        
    @property
    def text(self):
        return self._text
        
    @text.setter
    def text(self, new_text):
        self._text = new_text
        self._update_dimensions()
        
    def _update_dimensions(self):
        text_surface = self.font.render(self._text, True, self.color)
        self.rect.width = text_surface.get_width()
        self.rect.height = text_surface.get_height()
        
    def render(self, surface):
        if not self.visible:
            return
            
        text_surface = self.font.render(self._text, True, self.color)
        surface.blit(text_surface, self.rect)

class ProgressBar(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, 
                 value: float = 1.0, color: Tuple[int, int, int] = (0, 200, 0)):
        super().__init__(x, y, width, height)
        self.value = max(0.0, min(1.0, value))  # Clamp between 0 and 1
        self.color = color
        
    def set_value(self, value: float):
        self.value = max(0.0, min(1.0, value))  # Clamp between 0 and 1
        
    def render(self, surface):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        
        # Draw filled portion
        filled_width = int(self.rect.width * self.value)
        if filled_width > 0:
            filled_rect = pygame.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
            pygame.draw.rect(surface, self.color, filled_rect)
            
        # Draw border
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1)

def draw_text(surface, text, pos, color=(255, 255, 255), font_size=24):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_health_bar(surface, x, y, width, height, value, max_value, color=(0, 200, 0)):
    # Calculate percentage
    percentage = value / max_value if max_value > 0 else 0
    
    # Draw background
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (50, 50, 50), bg_rect)
    
    # Draw filled portion
    filled_width = int(width * percentage)
    if filled_width > 0:
        filled_rect = pygame.Rect(x, y, filled_width, height)
        pygame.draw.rect(surface, color, filled_rect)
        
    # Draw border
    pygame.draw.rect(surface, (200, 200, 200), bg_rect, 1)
    
    # Draw text
    font = pygame.font.SysFont(None, 20)
    text = f"{value}/{max_value}"
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    surface.blit(text_surface, text_rect)
    
class Slider(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, min_value: float = 0.0, 
                 max_value: float = 1.0, initial_value: float = 0.5, 
                 callback: Callable = None, label: str = ""):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self._value = max(min_value, min(max_value, initial_value))
        self.callback = callback
        self.label = label
        self.dragging = False
        self.handle_radius = height // 2
        self.track_height = max(4, height // 3)
        self.ui_manager = None
        
    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, new_value):
        old_value = self._value
        self._value = max(self.min_value, min(self.max_value, new_value))
        if self.callback and old_value != self._value:
            self.callback(self._value)
            
    def get_handle_position(self):
        value_range = self.max_value - self.min_value
        if value_range == 0:
            percentage = 0
        else:
            percentage = (self._value - self.min_value) / value_range
            
        return self.rect.x + int(percentage * (self.rect.width - 2 * self.handle_radius)) + self.handle_radius
    
    def set_value_from_position(self, x_pos):
        rel_x = max(self.rect.x + self.handle_radius, min(x_pos, self.rect.x + self.rect.width - self.handle_radius))
        percentage = (rel_x - (self.rect.x + self.handle_radius)) / (self.rect.width - 2 * self.handle_radius)
        self.value = self.min_value + percentage * (self.max_value - self.min_value)
        
    def handle_event(self, event) -> bool:
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_pos = self.get_handle_position()
            handle_rect = pygame.Rect(handle_pos - self.handle_radius, self.rect.y, 
                                    self.handle_radius * 2, self.rect.height)
                                    
            if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.set_value_from_position(event.pos[0])
                if self.ui_manager:
                    self.ui_manager.play_drop_sound()
                return True
                
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.set_value_from_position(event.pos[0])
            return True
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging:
            self.dragging = False
            return True
            
        return False
        
    def render(self, surface):
        if not self.visible:
            return
            
        # Draw label if exists
        if self.label:
            font = pygame.font.SysFont(None, 24)
            label_surface = font.render(self.label, True, (220, 220, 220))
            surface.blit(label_surface, (self.rect.x, self.rect.y - 25))
            
        # Draw track
        track_y = self.rect.y + (self.rect.height - self.track_height) // 2
        track_rect = pygame.Rect(self.rect.x + self.handle_radius, track_y, 
                               self.rect.width - 2 * self.handle_radius, self.track_height)
        pygame.draw.rect(surface, (80, 80, 80), track_rect)
        
        # Draw filled portion of track
        handle_pos = self.get_handle_position()
        filled_width = handle_pos - self.rect.x
        if filled_width > self.handle_radius:
            filled_rect = pygame.Rect(self.rect.x + self.handle_radius, track_y, 
                                    filled_width - self.handle_radius, self.track_height)
            pygame.draw.rect(surface, (100, 100, 200), filled_rect)
        
        # Draw handle
        handle_rect = pygame.Rect(handle_pos - self.handle_radius, self.rect.y, 
                                self.handle_radius * 2, self.rect.height)
        pygame.draw.circle(surface, (150, 150, 220), (handle_pos, self.rect.y + self.rect.height // 2), 
                         self.handle_radius)
        
        # Draw value text
        value_text = f"{int(self._value * 100)}%" if self.max_value == 1.0 else f"{self._value:.1f}"
        font = pygame.font.SysFont(None, 20)
        text_surface = font.render(value_text, True, (220, 220, 220))
        text_rect = text_surface.get_rect(midleft=(self.rect.right + 10, self.rect.y + self.rect.height // 2))
        surface.blit(text_surface, text_rect)
