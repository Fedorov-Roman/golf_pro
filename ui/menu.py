import pygame
import config
import core.records as records


def draw_menu(screen, state, buttons, message, font_large, font, small_font):
    width = config.SCREEN_WIDTH
    height = config.SCREEN_HEIGHT
    gradient_surf = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(
            config.MENU_GRADIENT_TOP[0] * (1 - ratio)
            + config.MENU_GRADIENT_BOTTOM[0] * ratio
        )
        g = int(
            config.MENU_GRADIENT_TOP[1] * (1 - ratio)
            + config.MENU_GRADIENT_BOTTOM[1] * ratio
        )
        b = int(
            config.MENU_GRADIENT_TOP[2] * (1 - ratio)
            + config.MENU_GRADIENT_BOTTOM[2] * ratio
        )
        pygame.draw.line(gradient_surf, (r, g, b), (0, y), (width, y))
    screen.blit(gradient_surf, (0, 0))

    pygame.draw.line(screen, config.WHITE, (0, 120), (width, 120), 2)
    pygame.draw.line(screen, config.WHITE, (0, height - 80), (width, height - 80), 2)

    title_shadow = font_large.render("ПРО ГОЛЬФ", True, (0, 0, 0))
    title = font_large.render("ПРО ГОЛЬФ", True, config.WHITE)
    title_rect = title.get_rect(center=(width // 2, 60))
    screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
    screen.blit(title, title_rect)

    if message:
        msg_bg = pygame.Surface((600, 50), pygame.SRCALPHA)
        msg_bg.fill((0, 0, 0, 150))
        msg_rect = msg_bg.get_rect(center=(width // 2, 150))
        screen.blit(msg_bg, msg_rect)
        msg = small_font.render(message, True, config.YELLOW)
        screen.blit(msg, msg.get_rect(center=(width // 2, 150)))

    mouse_pos = pygame.mouse.get_pos()
    for btn in buttons:
        btn.update(mouse_pos)
        btn.draw(screen, font)


def draw_game_over_background(
    screen, font_large, font, small_font, totals, num_players
):
    width = config.SCREEN_WIDTH
    height = config.SCREEN_HEIGHT

    gradient_surf = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(
            config.MENU_GRADIENT_TOP[0] * (1 - ratio)
            + config.MENU_GRADIENT_BOTTOM[0] * ratio
        )
        g = int(
            config.MENU_GRADIENT_TOP[1] * (1 - ratio)
            + config.MENU_GRADIENT_BOTTOM[1] * ratio
        )
        b = int(
            config.MENU_GRADIENT_TOP[2] * (1 - ratio)
            + config.MENU_GRADIENT_BOTTOM[2] * ratio
        )
        pygame.draw.line(gradient_surf, (r, g, b), (0, y), (width, y))
    screen.blit(gradient_surf, (0, 0))

    pygame.draw.line(screen, config.WHITE, (0, 120), (width, 120), 2)
    pygame.draw.line(screen, config.WHITE, (0, height - 80), (width, height - 80), 2)

    title_shadow = font_large.render("Игра окончена!", True, (0, 0, 0))
    title = font_large.render("Игра окончена!", True, config.WHITE)
    title_rect = title.get_rect(center=(width // 2, 60))
    screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
    screen.blit(title, title_rect)

    header = font.render("Игрок | Сумма ударов", True, config.WHITE)
    header_rect = header.get_rect(center=(width // 2, 170))
    screen.blit(header, header_rect)

    y = 220
    min_total = min(totals)
    for p in range(num_players):
        line = f"Игрок {p+1} : {totals[p]}"
        col = config.YELLOW if totals[p] == min_total else config.WHITE
        text = font.render(line, True, col)
        text_rect = text.get_rect(center=(width // 2, y))
        bg_rect = text_rect.inflate(200, 10)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 120))
        screen.blit(bg_surf, bg_rect)
        screen.blit(text, text_rect)
        y += 45

    winner = totals.index(min_total)
    win_text = font_large.render(f"Победитель: Игрок {winner+1}!", True, config.YELLOW)
    win_rect = win_text.get_rect(center=(width // 2, y + 10))
    win_shadow = font_large.render(f"Победитель: Игрок {winner+1}!", True, (0, 0, 0))
    screen.blit(win_shadow, (win_rect.x + 3, win_rect.y + 3))
    screen.blit(win_text, win_rect)


def draw_records_screen(
    screen, font_large, font, small_font, buttons, message, scroll_offset
):
    width = config.SCREEN_WIDTH
    height = config.SCREEN_HEIGHT

    # Градиентный фон
    gradient_surf = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(
            config.MENU_GRADIENT_TOP[0] * (1 - ratio)
            + config.MENU_GRADIENT_BOTTOM[0] * ratio
        )
        g = int(
            config.MENU_GRADIENT_TOP[1] * (1 - ratio)
            + config.MENU_GRADIENT_BOTTOM[1] * ratio
        )
        b = int(
            config.MENU_GRADIENT_TOP[2] * (1 - ratio)
            + config.MENU_GRADIENT_BOTTOM[2] * ratio
        )
        pygame.draw.line(gradient_surf, (r, g, b), (0, y), (width, y))
    screen.blit(gradient_surf, (0, 0))

    # Белые линии
    upper_line_y = 120
    lower_line_y = height - 80
    pygame.draw.line(screen, config.WHITE, (0, upper_line_y), (width, upper_line_y), 2)
    pygame.draw.line(screen, config.WHITE, (0, lower_line_y), (width, lower_line_y), 2)

    # Заголовок
    title_shadow = font_large.render("РЕКОРДЫ", True, (0, 0, 0))
    title = font_large.render("РЕКОРДЫ", True, config.WHITE)
    title_rect = title.get_rect(center=(width // 2, 60))
    screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
    screen.blit(title, title_rect)

    all_records = records.load_records()
    fields = ["forest", "desert", "snow"]
    weathers = ["sunny", "rain", "windy"]
    hole_counts = [3, 6, 9]
    field_names = {"forest": "Лес", "desert": "Пустыня", "snow": "Снег"}
    weather_names = {"sunny": "Солнечно", "rain": "Дождь", "windy": "Ветрено"}

    # Параметры контента
    start_y = 20  # отступ от верхнего края прокручиваемой области
    row_height = 30
    header_height = 35
    gap = 15
    bottom_padding = 20

    # Вычисляем полную высоту контента
    total_height = start_y
    for holes in hole_counts:
        total_height += header_height
        for field in fields:
            for weather in weathers:
                total_height += row_height
        total_height += gap
    total_height = total_height - gap + bottom_padding

    # Видимая область между линиями
    visible_top = upper_line_y + 2
    visible_bottom = lower_line_y - 2
    visible_height = visible_bottom - visible_top

    max_offset = max(0, total_height - visible_height)
    corrected_offset = max(0, min(scroll_offset, max_offset))

    # Поверхность для контента (без смещения)
    scroll_surf = pygame.Surface((width, total_height), pygame.SRCALPHA)
    scroll_surf.fill((0, 0, 0, 0))

    small_font_for_records = pygame.font.Font(None, 28)

    # Рисуем контент на scroll_surf, начиная с start_y
    y = start_y
    for holes in hole_counts:
        header_text = f"=== {holes} лунки ==="
        header_surf = font.render(header_text, True, config.YELLOW)
        header_rect = header_surf.get_rect(center=(width // 2, y))
        scroll_surf.blit(header_surf, header_rect)
        y += header_height

        for field in fields:
            for weather in weathers:
                key = f"{field}_{weather}_{holes}"
                if key in all_records:
                    rec = all_records[key]
                    text = f"{field_names[field]} / {weather_names[weather]}: {rec['winner']} — {rec['strokes']} ударов"
                else:
                    text = (
                        f"{field_names[field]} / {weather_names[weather]}: нет рекорда"
                    )
                txt_surf = small_font_for_records.render(text, True, config.WHITE)
                txt_rect = txt_surf.get_rect(topleft=(width // 2 - 300, y))
                bg_rect = txt_rect.inflate(20, 8)
                bg_surf = pygame.Surface(
                    (bg_rect.width, bg_rect.height), pygame.SRCALPHA
                )
                bg_surf.fill((0, 0, 0, 150))
                scroll_surf.blit(bg_surf, bg_rect)
                scroll_surf.blit(txt_surf, txt_rect)
                y += row_height
        y += gap

    # Отображаем прокрученную область
    screen.blit(
        scroll_surf, (0, visible_top), (0, corrected_offset, width, visible_height)
    )

    # Кнопка "Назад"
    mouse_pos = pygame.mouse.get_pos()
    for btn in buttons:
        btn.update(mouse_pos)
        btn.draw(screen, font)

    if message:
        msg = small_font.render(message, True, config.YELLOW)
        screen.blit(msg, (width // 2 - msg.get_width() // 2, 100))

    # Полоса прокрутки
    if total_height > visible_height:
        scroll_bar_x = width - 20
        scroll_bar_top = visible_top
        scroll_bar_bottom = visible_bottom
        scroll_bar_height = scroll_bar_bottom - scroll_bar_top
        pygame.draw.rect(
            screen, config.GRAY, (scroll_bar_x, scroll_bar_top, 10, scroll_bar_height)
        )
        thumb_height = max(30, scroll_bar_height * (visible_height / total_height))
        thumb_pos = scroll_bar_top + (scroll_bar_height - thumb_height) * (
            corrected_offset / max_offset
        )
        pygame.draw.rect(
            screen, config.WHITE, (scroll_bar_x, thumb_pos, 10, thumb_height)
        )

    return total_height, corrected_offset
