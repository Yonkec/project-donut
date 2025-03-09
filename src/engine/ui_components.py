import pygame
from typing import Callable, Tuple

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 action: Callable = None, color: Tuple[int, int, int] = (80, 80, 180)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = (120, 120, 220)
        self.hovered = False
        self.ui_manager = None
        
    def draw(self, screen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        font = pygame.font.SysFont(None, 32)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                if self.ui_manager and hasattr(self.ui_manager, 'audio_manager'):
                    self.ui_manager.audio_manager.play_ui_click()
                self.action()
                return True
        return False

def draw_text(screen, text, font_size, color, x, y):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def draw_health_bar(screen, x, y, width, height, current, maximum, color, outline_color=(50, 50, 50), text_color=(255, 255, 255)):
    outline_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, outline_color, outline_rect)
    
    if current > 0:
        fill_width = int((current / maximum) * width)
        fill_rect = pygame.Rect(x, y, fill_width, height)
        pygame.draw.rect(screen, color, fill_rect)
    
    pygame.draw.rect(screen, text_color, outline_rect, 2)
    
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"{current}/{maximum}", True, text_color)
    text_rect = text.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text, text_rect)
