import pygame
import random
import math


def make_tee_texture(radius, color):
    """Создаёт текстуру Tee (круг без обводки)."""
    size = radius * 2 + 10
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    pygame.draw.circle(surf, color, (cx, cy), radius)
    return surf


def make_green_texture(radius, fill_color, outline_color):
    """Создаёт текстуру Green (круг с толстой обводкой цвета фервея)."""
    size = radius * 2 + 10
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    pygame.draw.circle(surf, fill_color, (cx, cy), radius)
    pygame.draw.circle(surf, outline_color, (cx, cy), radius, 5)
    return surf


def make_rough_texture(radius, color):
    """
    Создаёт текстуру высокой травы с реалистичной растительностью.
    Пятно: круг с зашумлёнными краями, затемнённые травинки внутри.
    """
    size = radius * 2 + 20
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    # Основной контур пятна (полигон с волнистыми краями)
    points = []
    num_points = random.randint(12, 18)
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points + random.uniform(-0.2, 0.2)
        r = radius + random.randint(-8, 8)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((int(x), int(y)))
    if len(points) > 2:
        pygame.draw.polygon(surf, color, points)

    # Травинки внутри пятна (светлые и тёмные)
    for _ in range(random.randint(20, 30)):
        x1 = random.randint(cx - radius, cx + radius)
        y1 = random.randint(cy - radius, cy + radius)
        # Проверяем, что точка примерно внутри контура
        if math.hypot(x1 - cx, y1 - cy) > radius * 0.9:
            continue
        angle = random.uniform(0, 2 * math.pi)
        length = random.randint(3, 10)
        x2 = x1 + length * math.cos(angle)
        y2 = y1 + length * math.sin(angle)
        # Чередуем светлые и тёмные травинки
        if random.random() < 0.6:
            # Тёмная травинка
            shade = (
                max(0, color[0] - random.randint(20, 40)),
                max(0, color[1] - random.randint(20, 40)),
                max(0, color[2] - random.randint(20, 40)),
            )
        else:
            # Светлая травинка
            shade = (
                min(255, color[0] + random.randint(10, 30)),
                min(255, color[1] + random.randint(10, 30)),
                min(255, color[2] + random.randint(10, 30)),
            )
        pygame.draw.line(surf, shade, (int(x1), int(y1)), (int(x2), int(y2)), 1)

    return surf
