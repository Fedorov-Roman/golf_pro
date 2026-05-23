import pygame
import math
import config


def draw_wind_indicator(screen, wind):
    mag = math.hypot(wind[0], wind[1])
    if mag < 1:
        return
    angle = math.atan2(wind[1], wind[0])
    start_x, start_y = config.SCREEN_WIDTH - 120, 80
    length = min(50, mag / 4)
    end_x = start_x + math.cos(angle) * length
    end_y = start_y + math.sin(angle) * length
    pygame.draw.line(screen, config.WHITE, (start_x, start_y), (end_x, end_y), 3)
    arr_angle = math.atan2(end_y - start_y, end_x - start_x)
    L = 10
    left = (
        end_x + math.cos(arr_angle + math.pi * 0.75) * L,
        end_y + math.sin(arr_angle + math.pi * 0.75) * L,
    )
    right = (
        end_x + math.cos(arr_angle - math.pi * 0.75) * L,
        end_y + math.sin(arr_angle - math.pi * 0.75) * L,
    )
    pygame.draw.polygon(screen, config.WHITE, [left, (end_x, end_y), right])
    font = pygame.font.Font(None, 24)
    txt = font.render("Ветер", True, config.WHITE)
    screen.blit(txt, (start_x - 10, start_y - 20))


def draw_ui_panel(screen, game):
    ui_rect = pygame.Rect(0, config.SCREEN_HEIGHT - 100, config.SCREEN_WIDTH, 100)
    ui_surf = pygame.Surface((config.SCREEN_WIDTH, 100), pygame.SRCALPHA)
    ui_surf.fill((0, 0, 0, 180))
    screen.blit(ui_surf, ui_rect)
    pygame.draw.rect(screen, config.WHITE, ui_rect, 2)

    for idx, club in enumerate(config.CLUBS):
        icon_x = config.SCREEN_WIDTH - 250 + idx * 50
        icon_y = config.SCREEN_HEIGHT - 80
        pygame.draw.rect(screen, club.icon_color, (icon_x, icon_y, 30, 30))
        if idx == game.session.player_clubs[game.session.active_player]:
            pygame.draw.rect(screen, config.YELLOW, (icon_x - 2, icon_y - 2, 34, 34), 3)
        key_lbl = game.small_font.render(str(idx + 1), True, config.WHITE)
        screen.blit(key_lbl, (icon_x + 5, icon_y + 5))

    info = [
        f"Лунка: {game.current_hole + 1}/{game.num_holes}",
        f"Игрок: {game.session.active_player + 1}",
        f"Клюшка: {config.CLUBS[game.session.player_clubs[game.session.active_player]].name}",
        f"Удары: {game.session.strokes[game.session.active_player][game.current_hole]}",
    ]
    for i, line in enumerate(info):
        txt = game.small_font.render(line, True, config.WHITE)
        screen.blit(txt, (20, config.SCREEN_HEIGHT - 90 + i * 20))

    if game.message:
        font = pygame.font.Font(None, 36)
        msg = font.render(game.message, True, config.RED)
        screen.blit(
            msg,
            (
                config.SCREEN_WIDTH // 2 - msg.get_width() // 2,
                config.SCREEN_HEIGHT - 150,
            ),
        )
