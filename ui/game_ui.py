import pygame
import math
import config
from ui.hud import draw_ui_panel, draw_wind_indicator


def draw_game(screen, game):
    hole = game.holes_data[game.current_hole]
    screen.blit(game.hole_backgrounds[game.current_hole], (0, 0))

    t = pygame.time.get_ticks() / 1000.0
    # Анимированная вода
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
                sz = 5 + int(3 * math.sin(t * 4 + i))
                wave_surf = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(
                    wave_surf, (255, 255, 255, alpha), (0, 0, sz * 2, sz)
                )
                sx, sy = game.camera.world_to_screen((bx - sz, by - sz // 2))
                screen.blit(wave_surf, (int(sx), int(sy)))

    # Флаг с анимацией
    flag_img = game.textures["flag"]
    hole_pos = hole["hole"]
    wind = hole["wind"]
    wind_strength = math.hypot(wind[0], wind[1]) / 50.0
    flag_x, flag_y = hole_pos[0], hole_pos[1] - 45
    pole_base = game.camera.world_to_screen((flag_x, flag_y + 45))
    pole_top = game.camera.world_to_screen((flag_x, flag_y))
    wave1 = math.sin(t * 6) * 4 * wind_strength
    wave2 = math.cos(t * 5 + 1) * 3 * wind_strength
    flag_points = [
        game.camera.world_to_screen((flag_x, flag_y - 5)),
        game.camera.world_to_screen((flag_x + 14 + wave1, flag_y + 4)),
        game.camera.world_to_screen((flag_x, flag_y + 13 + wave2)),
    ]
    pygame.draw.line(screen, (180, 180, 180), pole_base, pole_top, 3)
    pygame.draw.polygon(screen, (220, 50, 50), flag_points)
    pygame.draw.polygon(screen, (0, 0, 0), flag_points, 1)

    # Лунка
    hole_img = game.textures["hole"]
    hx, hy = game.camera.world_to_screen((hole_pos[0] - 15, hole_pos[1] - 15))
    screen.blit(hole_img, (int(hx), int(hy)))

    draw_wind_indicator(screen, wind)
    game.particle_system.draw(screen)

    # Мячи
    for i, ball in enumerate(game.balls):
        if ball.visible and not ball.in_hole:
            shadow_offset = ball.z * 0.5
            shadow_pos = game.camera.world_to_screen(
                (ball.pos[0] - 12 + shadow_offset, ball.pos[1] - 6 + shadow_offset)
            )
            screen.blit(game.ball_shadow, (int(shadow_pos[0]), int(shadow_pos[1])))

            ball_y = ball.pos[1] - ball.z
            ball_img = game.ball_surfs_colored[ball.player_index]
            w, h = ball_img.get_width(), ball_img.get_height()
            bx, by = game.camera.world_to_screen(
                (ball.pos[0] - w // 2, ball_y - h // 2)
            )
            screen.blit(ball_img, (int(bx), int(by)))

    # Выбор угла
    if game.shot_system.selecting_angle:
        draw_angle_selector(screen, game)

    # Прицеливание
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
                sx, sy = game.camera.world_to_screen((px, py))
                s = pygame.Surface((4, 4), pygame.SRCALPHA)
                s.fill((255, 0, 0, alpha))
                screen.blit(s, (int(sx) - 2, int(sy) - 2))
            percent = int(power / max_power * 100)
            force_text = game.small_font.render(f"{percent}%", True, config.BLACK)
            ex, ey = game.camera.world_to_screen(end_world)
            screen.blit(force_text, (int(ex) + 10, int(ey) - 15))

    draw_ui_panel(screen, game)


def draw_angle_selector(screen, game):
    ball = game.balls[game.session.active_player]
    cx, cy = int(ball.pos[0]), int(ball.pos[1])
    radius = config.ANGLE_SELECT_RADIUS

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
