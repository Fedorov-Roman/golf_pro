import pygame
import math
import random


def make_tree(radius=45, leaf_color=(0, 100, 0)):
    size = int(radius * 2.5) + 20
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    trunk_w = int(radius * 0.3)
    trunk_h = int(radius * 1.1)
    trunk_rect = pygame.Rect(cx - trunk_w // 2, cy + radius * 0.15, trunk_w, trunk_h)
    # Текстура коры
    for i in range(trunk_w):
        shade = int(100 + 60 * i / trunk_w)
        color = (shade, 70, 20)
        pygame.draw.line(
            surf,
            color,
            (trunk_rect.left + i, trunk_rect.top),
            (trunk_rect.left + i, trunk_rect.bottom),
        )
    # Линии коры
    for _ in range(6):
        x = random.randint(trunk_rect.left + 2, trunk_rect.right - 2)
        y = random.randint(trunk_rect.top, trunk_rect.bottom - 5)
        pygame.draw.line(
            surf, (80, 50, 20), (x, y), (x + random.randint(-3, 3), y + 5), 1
        )
    # Ветки
    branch_angles = [45, 135, 225, 315]
    for angle in branch_angles:
        rad = math.radians(angle)
        length = radius * 0.8
        end_x = cx + length * math.cos(rad)
        end_y = cy - trunk_h * 0.4 + length * math.sin(rad)
        pygame.draw.line(
            surf, (101, 67, 33), (cx, cy - trunk_h * 0.3), (end_x, end_y), 4
        )
    # Многослойная листва (без чёрного контура)
    # Задние слои (более тёмные)
    for ang in range(0, 360, 40):
        rad_ang = math.radians(ang)
        off_x = radius * 0.7 * math.cos(rad_ang)
        off_y = radius * 0.7 * math.sin(rad_ang) - radius * 0.3
        darker = (
            max(0, leaf_color[0] - 30),
            max(0, leaf_color[1] - 20),
            max(0, leaf_color[2] - 20),
        )
        pygame.draw.circle(surf, darker, (cx + off_x, cy + off_y), int(radius * 0.55))
    # Основной купол
    pygame.draw.circle(surf, leaf_color, (cx, cy - radius * 0.3), radius)
    for ang in range(0, 360, 72):
        rad_ang = math.radians(ang)
        off_x = radius * 0.55 * math.cos(rad_ang)
        off_y = radius * 0.55 * math.sin(rad_ang) - radius * 0.3
        pygame.draw.circle(
            surf, leaf_color, (cx + off_x, cy + off_y), int(radius * 0.6)
        )
        # Светлые блики
        lighter = (
            min(255, leaf_color[0] + 20),
            min(255, leaf_color[1] + 10),
            min(255, leaf_color[2] + 10),
        )
        pygame.draw.circle(
            surf, lighter, (cx + off_x - 2, cy + off_y - 2), int(radius * 0.2)
        )
    return surf


def make_bush(radius=30):
    size = radius * 2 + 20
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    branch_color = (139, 90, 43)
    # Ветки
    for _ in range(12):
        angle = random.uniform(0, 2 * math.pi)
        length = random.uniform(radius * 0.5, radius)
        end_x = cx + length * math.cos(angle)
        end_y = cy + length * math.sin(angle)
        mid_angle = angle + random.uniform(-0.5, 0.5)
        mid_len = length * 0.6
        mid_x = cx + mid_len * math.cos(mid_angle)
        mid_y = cy + mid_len * math.sin(mid_angle)
        points = [(cx, cy), (mid_x, mid_y), (end_x, end_y)]
        pygame.draw.lines(surf, branch_color, False, points, 3)
    # Листва (множество кружков)
    for _ in range(20):
        ang = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, radius * 0.8)
        lx = cx + dist * math.cos(ang)
        ly = cy + dist * math.sin(ang)
        shade = random.randint(80, 130)
        pygame.draw.circle(surf, (shade, 50, 20, 200), (lx, ly), random.randint(4, 8))
    return surf


def make_rock(radius=20):
    size = radius * 2 + 20
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    points = []
    num_points = random.randint(10, 16)
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points + random.uniform(-0.1, 0.1)
        r = radius + random.randint(-5, 5)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    if len(points) > 2:
        base_col = (
            random.randint(130, 160),
            random.randint(110, 130),
            random.randint(90, 110),
        )
        pygame.draw.polygon(surf, base_col, points)
        # Блики и тени
        highlight = (
            min(255, base_col[0] + 30),
            min(255, base_col[1] + 30),
            min(255, base_col[2] + 30),
        )
        shadow = (
            max(0, base_col[0] - 30),
            max(0, base_col[1] - 30),
            max(0, base_col[2] - 30),
        )
        # Рисуем несколько трещин (линии)
        for _ in range(3):
            p1 = random.choice(points)
            p2 = (
                cx + random.randint(-radius // 2, radius // 2),
                cy + random.randint(-radius // 2, radius // 2),
            )
            pygame.draw.line(surf, shadow, p1, p2, 1)
        # Легкий блик в верхней части
        top_points = sorted(points, key=lambda p: p[1])[: len(points) // 2]
        if top_points:
            avg_x = sum(p[0] for p in top_points) / len(top_points)
            avg_y = sum(p[1] for p in top_points) / len(top_points)
            pygame.draw.circle(
                surf, highlight, (int(avg_x), int(avg_y)), radius // 3, 0
            )
    return surf


def make_ice_block(radius=40):
    size = radius * 2 + 40
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    points = []
    for angle in range(0, 360, 30):
        r = radius + random.randint(-6, 6)
        x = cx + r * math.cos(math.radians(angle))
        y = cy + r * math.sin(math.radians(angle))
        points.append((x, y))
    if len(points) > 2:
        # Полупрозрачный голубой
        pygame.draw.polygon(surf, (173, 216, 230, 180), points)
        # Внутренние трещины
        for _ in range(5):
            start_ang = random.uniform(0, 2 * math.pi)
            start_r = random.uniform(0, radius * 0.5)
            sx = cx + start_r * math.cos(start_ang)
            sy = cy + start_r * math.sin(start_ang)
            end_ang = start_ang + random.uniform(-0.5, 0.5)
            end_r = radius * 0.9
            ex = cx + end_r * math.cos(end_ang)
            ey = cy + end_r * math.sin(end_ang)
            pygame.draw.line(surf, (255, 255, 255, 150), (sx, sy), (ex, ey), 1)
        # Объёмная снежная шапка
        cap_center_y = cy - radius * 0.5
        for _ in range(8):
            off_x = random.randint(-int(radius * 0.6), int(radius * 0.6))
            off_y = random.randint(-int(radius * 0.3), int(radius * 0.3))
            cap_r = random.randint(int(radius * 0.2), int(radius * 0.5))
            alpha = random.randint(150, 220)
            col = (255, 255, 255, alpha)
            pygame.draw.circle(surf, col, (cx + off_x, cap_center_y + off_y), cap_r)
    return surf
