import pygame
import math


def make_ball():
    size = 24
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    for r in range(9, 0, -1):
        alpha = 255 - int(30 * (9 - r) / 9)
        pygame.draw.circle(surf, (255, 255, 255, alpha), (cx, cy), r)
    for i in range(8):
        ang = i * 45 * math.pi / 180
        dx = 6 * math.cos(ang)
        dy = 6 * math.sin(ang)
        pygame.draw.circle(surf, (200, 200, 200, 180), (cx + dx, cy + dy), 2)
    pygame.draw.circle(surf, (255, 255, 255, 220), (cx - 3, cy - 4), 3)
    pygame.draw.circle(surf, (50, 50, 50, 200), (cx, cy), 9, 1)
    return surf


def make_colored_ball(color):
    size = 24
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    for r in range(9, 0, -1):
        t = r / 9.0
        base = (
            int(color[0] * t + 255 * (1 - t)),
            int(color[1] * t + 255 * (1 - t)),
            int(color[2] * t + 255 * (1 - t)),
        )
        alpha = 255
        pygame.draw.circle(surf, base + (alpha,), (cx, cy), r)
    for i in range(8):
        ang = i * 45 * math.pi / 180
        dx = 6 * math.cos(ang)
        dy = 6 * math.sin(ang)
        dark = (
            max(0, color[0] - 40),
            max(0, color[1] - 40),
            max(0, color[2] - 40),
            220,
        )
        pygame.draw.circle(surf, dark, (cx + dx, cy + dy), 2)
    pygame.draw.circle(surf, (255, 255, 255, 240), (cx - 3, cy - 4), 3)
    pygame.draw.circle(surf, (50, 50, 50, 220), (cx, cy), 9, 1)
    return surf


def make_flag():
    surf = pygame.Surface((24, 50), pygame.SRCALPHA)
    pygame.draw.line(surf, (200, 200, 200), (12, 0), (12, 49), 3)
    # Флаг теперь будет рисоваться динамически, но для меню можно оставить статичный
    flag_points = [(12, 0), (24, 8), (12, 16)]
    pygame.draw.polygon(surf, (220, 50, 50), flag_points)
    pygame.draw.polygon(surf, (0, 0, 0), flag_points, 1)
    return surf


def make_hole_gfx():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    cx, cy = 15, 15
    # Внешний ободок земли
    pygame.draw.circle(surf, (101, 67, 33, 200), (cx, cy), 14)
    # Тень внутри
    pygame.draw.circle(surf, (0, 0, 0, 220), (cx, cy), 12)
    # Внутренняя тёмная область
    pygame.draw.circle(surf, (40, 40, 40, 220), (cx, cy), 9)
    pygame.draw.circle(surf, (0, 0, 0, 220), (cx, cy), 9, 1)
    return surf
