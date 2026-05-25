import pygame
import math
import random
import config


def make_bunker(radius=60, sand_color=(238, 203, 173)):
    size = radius * 2 + 30
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    points = []
    for angle in range(0, 360, 15):
        r = radius + random.randint(-8, 8)
        x = cx + r * math.cos(math.radians(angle))
        y = cy + r * math.sin(math.radians(angle))
        points.append((x, y))
    if len(points) > 2:
        pygame.draw.polygon(surf, sand_color, points)
        for _ in range(50):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius * 0.9)
            px = cx + dist * math.cos(ang)
            py = cy + dist * math.sin(ang)
            shade = random.randint(0, 30)
            col = (
                min(255, sand_color[0] + shade),
                min(255, sand_color[1] + shade),
                min(255, sand_color[2] + shade),
            )
            pygame.draw.circle(surf, col, (px, py), random.randint(1, 2))
        for _ in range(12):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius * 0.7)
            px = cx + dist * math.cos(ang)
            py = cy + dist * math.sin(ang)
            stone_col = (
                random.randint(100, 130),
                random.randint(80, 100),
                random.randint(50, 70),
            )
            pygame.draw.circle(surf, stone_col, (px, py), random.randint(2, 4))
    return surf


def make_water_smooth(radius=80, water_color=(65, 105, 225)):
    """
    Генерирует текстуру воды с плавными краями, составленную из нескольких кругов.
    Возвращает кортеж: (спрайт, список относительных кругов).
    Каждый круг в списке — (x, y, radius) относительно центра спрайта.
    """
    size = int(radius * 2.5)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    # Генерируем 4-8 кругов
    num_blobs = random.randint(4, 8)
    blobs_relative = []  # в координатах относительно центра спрайта
    for _ in range(num_blobs):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, radius * 0.4)
        bx = dist * math.cos(angle)
        by = dist * math.sin(angle)
        br = random.uniform(radius * 0.5, radius * 0.9)
        blobs_relative.append((bx, by, br))

    # Обводка всей фигуры: рисуем круги тёмным цветом чуть большего радиуса
    outline_color = (
        max(0, water_color[0] - 60),
        max(0, water_color[1] - 60),
        max(0, water_color[2] - 60),
        220,
    )
    outline_increase = 3
    for bx, by, br in blobs_relative:
        pygame.draw.circle(
            surf,
            outline_color,
            (int(cx + bx), int(cy + by)),
            int(br + outline_increase),
        )

    # Основная заливка (без внутренних тёмных кругов, чтобы не было внутренних границ)
    for bx, by, br in blobs_relative:
        pygame.draw.circle(
            surf, water_color + (200,), (int(cx + bx), int(cy + by)), int(br)
        )

    # Блики
    for _ in range(random.randint(4, 7)):
        ang = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, radius * 0.7)
        lx = cx + dist * math.cos(ang)
        ly = cy + dist * math.sin(ang)
        light_surf = pygame.Surface((12, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(
            light_surf, (255, 255, 255, random.randint(60, 120)), light_surf.get_rect()
        )
        rotated_light = pygame.transform.rotate(light_surf, random.randint(0, 360))
        surf.blit(
            rotated_light,
            (
                int(lx - rotated_light.get_width() / 2),
                int(ly - rotated_light.get_height() / 2),
            ),
        )

    return surf, blobs_relative


def make_ice_surface(radius=80):
    size = radius * 2 + 40
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    points = []
    num = 24
    for i in range(num):
        angle = 2 * math.pi * i / num
        r = radius + random.uniform(-5, 5)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    if len(points) > 2:
        pygame.draw.polygon(surf, config.ICE_COLOR + (140,), points)
    for _ in range(8):
        start_ang = random.uniform(0, 2 * math.pi)
        start_r = random.uniform(0, radius * 0.4)
        sx = cx + start_r * math.cos(start_ang)
        sy = cy + start_r * math.sin(start_ang)
        end_ang = start_ang + random.uniform(-0.4, 0.4)
        end_r = radius * 0.9
        ex = cx + end_r * math.cos(end_ang)
        ey = cy + end_r * math.sin(end_ang)
        pygame.draw.line(surf, (255, 255, 255, 180), (sx, sy), (ex, ey), 2)
        for _ in range(3):
            t = random.uniform(0.2, 0.8)
            bx = sx + (ex - sx) * t + random.randint(-8, 8)
            by = sy + (ey - sy) * t + random.randint(-8, 8)
            pygame.draw.line(
                surf,
                (255, 255, 255, 120),
                (bx, by),
                (bx + random.randint(-10, 10), by + random.randint(-10, 10)),
                1,
            )
    return surf
