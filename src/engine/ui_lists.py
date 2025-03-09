import pygame
from .ui_elements import UIElement

class ScrollableList(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, item_height: int = 40):
        super().__init__(x, y, width, height)
        self.items = []
        self.item_height = item_height
        self.scroll_offset = 0
        self.max_visible_items = height // item_height
        self.dragging = False
        self.drag_item = None
        self.drag_start_y = 0
        self.drag_offset_y = 0
        
    def add_item(self, item):
        self.items.append(item)
        
    def clear(self):
        self.items = []
        self.scroll_offset = 0
        
    def handle_event(self, event) -> bool:
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
                return True
            elif event.button == 5:  # Scroll down
                max_offset = max(0, len(self.items) - self.max_visible_items)
                self.scroll_offset = min(max_offset, self.scroll_offset + 1)
                return True
            elif event.button == 1:  # Left click
                if self.rect.collidepoint(event.pos):
                    # Check if clicking on an item
                    item_idx = self.get_item_at_position(event.pos)
                    if item_idx is not None:
                        # Start dragging
                        self.dragging = True
                        self.drag_item = item_idx
                        self.drag_start_y = event.pos[1]
                        self.drag_offset_y = 0
                    return True
                    
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging and self.drag_item is not None:
                # Update drag offset
                self.drag_offset_y = event.pos[1] - self.drag_start_y
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                if self.drag_item is not None and self.drag_offset_y != 0:
                    # Calculate new position
                    new_idx = self.get_drag_target_index(event.pos[1])
                    if new_idx is not None and new_idx != self.drag_item:
                        # Move item
                        item = self.items.pop(self.drag_item)
                        self.items.insert(new_idx, item)
                
                # Reset drag state
                self.dragging = False
                self.drag_item = None
                self.drag_offset_y = 0
                return True
                
        return False
        
    def get_item_at_position(self, pos):
        if not self.rect.collidepoint(pos):
            return None
            
        # Calculate item index
        rel_y = pos[1] - self.rect.y
        item_idx = self.scroll_offset + rel_y // self.item_height
        
        if 0 <= item_idx < len(self.items):
            return item_idx
        return None
        
    def get_drag_target_index(self, y_pos):
        if not self.rect.y <= y_pos <= self.rect.y + self.rect.height:
            return None
            
        # Calculate target index
        rel_y = y_pos - self.rect.y
        target_idx = self.scroll_offset + rel_y // self.item_height
        
        # Clamp to valid range
        return max(0, min(len(self.items) - 1, target_idx))
        
    def render(self, surface):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(surface, (30, 30, 30), self.rect)
        
        # Draw items
        for i in range(min(self.max_visible_items, len(self.items))):
            item_idx = i + self.scroll_offset
            if item_idx >= len(self.items):
                break
                
            item = self.items[item_idx]
            
            # Calculate item rect
            item_y = self.rect.y + i * self.item_height
            item_rect = pygame.Rect(self.rect.x, item_y, self.rect.width, self.item_height)
            
            # Draw item background
            bg_color = (50, 50, 50) if item_idx % 2 == 0 else (40, 40, 40)
            pygame.draw.rect(surface, bg_color, item_rect)
            
            # Draw item content
            if hasattr(item, 'render_in_list'):
                item.render_in_list(surface, self.rect.x, item_y, self.rect.width, self.item_height)
            else:
                # Default rendering for items without custom rendering
                font = pygame.font.SysFont(None, 24)
                text = str(item)
                text_surface = font.render(text, True, (220, 220, 220))
                surface.blit(text_surface, (self.rect.x + 10, item_y + (self.item_height - text_surface.get_height()) // 2))
        
        # Draw dragged item if dragging
        if self.dragging and self.drag_item is not None:
            item = self.items[self.drag_item]
            
            # Calculate dragged item position
            drag_y = self.rect.y + (self.drag_item - self.scroll_offset) * self.item_height + self.drag_offset_y
            drag_rect = pygame.Rect(self.rect.x, drag_y, self.rect.width, self.item_height)
            
            # Ensure dragged item stays within list bounds
            if drag_rect.y < self.rect.y:
                drag_rect.y = self.rect.y
            elif drag_rect.y + drag_rect.height > self.rect.y + self.rect.height:
                drag_rect.y = self.rect.y + self.rect.height - drag_rect.height
            
            # Draw dragged item with highlight
            pygame.draw.rect(surface, (70, 70, 100), drag_rect)
            if hasattr(item, 'render_in_list'):
                item.render_in_list(surface, self.rect.x, drag_rect.y, self.rect.width, self.item_height)
            else:
                font = pygame.font.SysFont(None, 24)
                text = str(item)
                text_surface = font.render(text, True, (220, 220, 220))
                surface.blit(text_surface, (self.rect.x + 10, drag_rect.y + (self.item_height - text_surface.get_height()) // 2))
        
        # Draw border
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 1)
        
        # Draw scroll indicators if needed
        if len(self.items) > self.max_visible_items:
            # Draw scroll up indicator
            if self.scroll_offset > 0:
                pygame.draw.polygon(surface, (200, 200, 200), [
                    (self.rect.right - 15, self.rect.y + 10),
                    (self.rect.right - 5, self.rect.y + 10),
                    (self.rect.right - 10, self.rect.y + 5)
                ])
                
            # Draw scroll down indicator
            if self.scroll_offset < len(self.items) - self.max_visible_items:
                pygame.draw.polygon(surface, (200, 200, 200), [
                    (self.rect.right - 15, self.rect.bottom - 10),
                    (self.rect.right - 5, self.rect.bottom - 10),
                    (self.rect.right - 10, self.rect.bottom - 5)
                ])
