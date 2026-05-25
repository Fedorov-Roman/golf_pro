import pygame
import math
import config
from ui.hud import draw_ui_panel, draw_wind_indicator


def draw_game(screen, game):
    hole = game.holes_data[game.current_hole]
    camera = game.camera
    bg_color = hole["preset"]["bg"]
    screen.fill(bg_color)

    # --- Рисуем rough-зоны (высокая трава) до фервея ---
    for zone in hole.get("zones", []):
        if zone.type == "rough" and "image" in zone.params:
            img = zone.params["image"]
            pos = zone.pos
            screen_pos = camera.world_to_screen(pos)
            if camera.zoom != 1.0:
                w = max(1, int(img.get_width() * camera.zoom))
                h = max(1, int(img.get_height() * camera.zoom))
                img_scaled = pygame.transform.scale(img, (w, h))
            else:
                img_scaled = img
            rect = img_scaled.get_rect(center=screen_pos)
            screen.blit(img_scaled, rect)

    # --- Фервей (рисуем после rough, чтобы был поверх) ---
    fairway_points = hole.get("fairway_points", [])
    if fairway_points and len(fairway_points) >= 2:
        if hole["field_type"] == "snow":
            fairway_color = (
                min(255, bg_color[0] + 10),
                min(255, bg_color[1] + 10),
                min(255, bg_color[2] + 10),
            )
        else:
            fairway_color = (
                max(0, bg_color[0] - 10),
                max(0, bg_color[1] - 10),
                max(0, bg_color[2] - 10),
            )
        half_width = config.FAIRWAY_WIDTH // 2
        left_boundary = []
        right_boundary = []
        for i in range(len(fairway_points)):
            if i == 0:
                dx = fairway_points[1][0] - fairway_points[0][0]
                dy = fairway_points[1][1] - fairway_points[0][1]
            elif i == len(fairway_points) - 1:
                dx = fairway_points[-1][0] - fairway_points[-2][0]
                dy = fairway_points[-1][1] - fairway_points[-2][1]
            else:
                dx1 = fairway_points[i][0] - fairway_points[i - 1][0]
                dy1 = fairway_points[i][1] - fairway_points[i - 1][1]
                dx2 = fairway_points[i + 1][0] - fairway_points[i][0]
                dy2 = fairway_points[i + 1][1] - fairway_points[i][1]
                dx = dx1 + dx2
                dy = dy1 + dy2
            length = math.hypot(dx, dy)
            if length == 0:
                if i > 0:
                    dx = fairway_points[i][0] - fairway_points[i - 1][0]
                    dy = fairway_points[i][1] - fairway_points[i - 1][1]
                    length = math.hypot(dx, dy)
                    if length == 0:
                        continue
                else:
                    continue
            nx = -dy / length
            ny = dx / length
            left_point = (
                fairway_points[i][0] + nx * half_width,
                fairway_points[i][1] + ny * half_width,
            )
            right_point = (
                fairway_points[i][0] - nx * half_width,
                fairway_points[i][1] - ny * half_width,
            )
            left_boundary.append(left_point)
            right_boundary.append(right_point)
        polygon_world = left_boundary + right_boundary[::-1]
        if len(polygon_world) >= 3:
            screen_points = [camera.world_to_screen(p) for p in polygon_world]
            pygame.draw.polygon(screen, fairway_color, screen_points)

    # --- Рисуем зоны Tee и Green поверх фервея ---
    for zone in hole.get("zones", []):
        if zone.type in ("tee", "green") and "image" in zone.params:
            img = zone.params["image"]
            pos = zone.pos
            screen_pos = camera.world_to_screen(pos)
            if camera.zoom != 1.0:
                w = max(1, int(img.get_width() * camera.zoom))
                h = max(1, int(img.get_height() * camera.zoom))
                img_scaled = pygame.transform.scale(img, (w, h))
            else:
                img_scaled = img
            rect = img_scaled.get_rect(center=screen_pos)
            screen.blit(img_scaled, rect)

    # --- Препятствия ---
    z_map = {"sand": 0, "water": 1, "ice": 1}
    sorted_obs = sorted(
        hole["obstacles"], key=lambda o: (z_map.get(o["type"], 2), o["pos"][1])
    )
    for obs in sorted_obs:
        img = obs["image"]
        pos = obs["pos"]
        screen_pos = camera.world_to_screen(pos)
        if camera.zoom != 1.0:
            w = max(1, int(img.get_width() * camera.zoom))
            h = max(1, int(img.get_height() * camera.zoom))
            img_scaled = pygame.transform.scale(img, (w, h))
        else:
            img_scaled = img
        rect = img_scaled.get_rect(center=screen_pos)
        screen.blit(img_scaled, rect)

    # --- Анимированная вода (блики) ---
    t = pygame.time.get_ticks() / 1000.0
    for obs in hole["obstacles"]:
        if obs["type"] == "water":
            cx, cy = obs["pos"]
            radius = obs["radius"]
            for i in range(6):
                angle = (t * 2 + i * 1.2) % (2 * math.pi)
                dist = radius * 0.7 * (0.7 + 0.3 * math.sin(t * 3 + i))
                bx = cx + dist * math.cos(angle)
                by = cy + dist * math.sin(angle)
                alpha = int(100 + 70 * math.sin(t * 5 + i))
                sz = int((5 + 3 * math.sin(t * 4 + i)) * camera.zoom)
                if sz > 0:
                    wave_surf = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(
                        wave_surf, (255, 255, 255, alpha), (0, 0, sz * 2, sz)
                    )
                    screen_pos = camera.world_to_screen((bx, by))
                    screen.blit(
                        wave_surf, (screen_pos[0] - sz, screen_pos[1] - sz // 2)
                    )

    # --- Флаг ---
    flag_img = game.textures["flag"]
    hole_pos = hole["hole"]
    wind = hole["wind"]
    wind_strength = math.hypot(wind[0], wind[1]) / 50.0
    flag_x, flag_y = hole_pos[0], hole_pos[1] - 45
    pole_base = camera.world_to_screen((flag_x, flag_y + 45))
    pole_top = camera.world_to_screen((flag_x, flag_y))
    wave1 = math.sin(t * 6) * 4 * wind_strength
    wave2 = math.cos(t * 5 + 1) * 3 * wind_strength
    flag_world_points = [
        (flag_x, flag_y - 5),
        (flag_x + 14 + wave1, flag_y + 4),
        (flag_x, flag_y + 13 + wave2),
    ]
    flag_screen_points = [camera.world_to_screen(p) for p in flag_world_points]
    pygame.draw.line(screen, (180, 180, 180), pole_base, pole_top, 3)
    pygame.draw.polygon(screen, (220, 50, 50), flag_screen_points)
    pygame.draw.polygon(screen, (0, 0, 0), flag_screen_points, 1)

    # --- Лунка (с масштабированием) ---
    hole_img = game.textures["hole"]
    hole_center_screen = camera.world_to_screen(hole_pos)
    if camera.zoom != 1.0:
        w = max(1, int(hole_img.get_width() * camera.zoom))
        h = max(1, int(hole_img.get_height() * camera.zoom))
        hole_img_scaled = pygame.transform.scale(hole_img, (w, h))
    else:
        hole_img_scaled = hole_img
    hole_rect = hole_img_scaled.get_rect(center=hole_center_screen)
    screen.blit(hole_img_scaled, hole_rect)

    # --- Частицы с учётом камеры ---
    game.particle_system.draw(screen, camera)

    # --- Ветер ---
    draw_wind_indicator(screen, wind)

    # --- Мячи ---
    for i, ball in enumerate(game.balls):
        if ball.visible and not ball.in_hole:
            shadow_offset = ball.z * 0.5 * camera.zoom
            shadow_world = (
                ball.pos[0] - 12 + shadow_offset,
                ball.pos[1] - 6 + shadow_offset,
            )
            shadow_screen = camera.world_to_screen(shadow_world)
            shadow_img = game.ball_shadow
            if camera.zoom != 1.0:
                sw = max(1, int(shadow_img.get_width() * camera.zoom))
                sh = max(1, int(shadow_img.get_height() * camera.zoom))
                shadow_img = pygame.transform.scale(shadow_img, (sw, sh))
            screen.blit(shadow_img, shadow_screen)

            ball_world = (ball.pos[0], ball.pos[1] - ball.z)
            ball_screen = camera.world_to_screen(ball_world)
            ball_img = game.ball_surfs_colored[ball.player_index]
            if camera.zoom != 1.0:
                bw = max(1, int(ball_img.get_width() * camera.zoom))
                bh = max(1, int(ball_img.get_height() * camera.zoom))
                ball_img = pygame.transform.scale(ball_img, (bw, bh))
            ball_rect = ball_img.get_rect(center=ball_screen)
            screen.blit(ball_img, ball_rect)

    # --- Выбор угла ---
    if game.shot_system.selecting_angle:
        draw_angle_selector(screen, game)

    # --- Прицеливание ---
    ball_active = game.balls[game.session.active_player]
    if (
        game.shot_system.is_aiming
        and not game.shot_system.selecting_angle
        and ball_active.visible
        and not ball_active.moving
    ):
        ball_pos = ball_active.pos
        acc_x, acc_y = game.shot_system.aim_accumulated
        dist = math.hypot(acc_x, acc_y)
        if dist > 5:
            direction = (acc_x / dist, acc_y / dist)
            max_power = config.CLUBS[game.session.current_club()].max_power
            power = min(dist * 1.8, max_power)
            line_len = power * 0.3
            end_world = (
                ball_pos[0] + direction[0] * line_len,
                ball_pos[1] + direction[1] * line_len,
            )
            for step in range(20):
                alpha = 255 - step * 12
                inter = step / 20
                px = ball_pos[0] + (end_world[0] - ball_pos[0]) * inter
                py = ball_pos[1] + (end_world[1] - ball_pos[1]) * inter
                sx, sy = camera.world_to_screen((px, py))
                s = pygame.Surface((4, 4), pygame.SRCALPHA)
                s.fill((255, 0, 0, alpha))
                screen.blit(s, (int(sx) - 2, int(sy) - 2))
            percent = int(power / max_power * 100)
            force_text = game.small_font.render(f"{percent}%", True, config.BLACK)
            ex, ey = camera.world_to_screen(end_world)
            screen.blit(force_text, (int(ex) + 10, int(ey) - 15))

    # --- HUD ---
    draw_ui_panel(screen, game)


def draw_angle_selector(screen, game):
    ball = game.balls[game.session.active_player]
    camera = game.camera
    ball_world = ball.pos
    ball_screen = camera.world_to_screen(ball_world)
    cx, cy = int(ball_screen[0]), int(ball_screen[1])
    # Окно выбора угла не должно масштабироваться при зуме камеры
    radius = config.ANGLE_SELECT_RADIUS  # фиксированный радиус

    ball_img = game.ball_surfs_colored[game.session.active_player]
    img_w, img_h = ball_img.get_width(), ball_img.get_height()

    scale = (2 * radius) / max(img_w, img_h)
    scaled_w = max(1, int(img_w * scale))
    scaled_h = max(1, int(img_h * scale))
    scaled_ball = pygame.transform.smoothscale(ball_img, (scaled_w, scaled_h))

    ball_rect = scaled_ball.get_rect(center=(cx, cy))
    screen.blit(scaled_ball, ball_rect)

    dy = (game.shot_system.angle_value / config.MAX_ANGLE) * radius
    indicator_y = cy + dy
    # Индикатор тоже фиксированного размера
    pygame.draw.circle(screen, config.RED, (cx, int(indicator_y)), 6)
    pygame.draw.circle(screen, config.WHITE, (cx, int(indicator_y)), 6, 1)

    angle_text = game.small_font.render(
        f"Угол: {int(game.shot_system.angle_value)}°", True, config.WHITE
    )
    screen.blit(angle_text, (cx - 40, cy - radius - 20))
    prompt = game.small_font.render(
        "Двигайте мышь вниз для подъёма", True, config.WHITE
    )
    screen.blit(prompt, (cx - 100, cy + radius + 10))
