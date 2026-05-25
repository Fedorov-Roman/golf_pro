import pygame

def make_tee_texture(radius, color):
    """Создаёт текстуру Tee (круг без обводки)."""
    size = radius * 2 + 10
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    # Заливка
    pygame.draw.circle(surf, color, (cx, cy), radius)
    return surf

def make_green_texture(radius, fill_color, outline_color):
    """Создаёт текстуру Green (круг с толстой обводкой цвета фервея)."""
    size = radius * 2 + 10
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    # Заливка
    pygame.draw.circle(surf, fill_color, (cx, cy), radius)
    # Толстая обводка
    pygame.draw.circle(surf, outline_color, (cx, cy), radius, 5)
    return surf
