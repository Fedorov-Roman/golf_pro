import pygame
import config


class Button:
    def __init__(
        self, rect, text, base_color, hover_color=None, text_color=config.BLACK
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color if hover_color else base_color
        self.text_color = text_color
        self.current_color = base_color

    def draw(self, surface, font):
        # Тень кнопки
        shadow_rect = self.rect.move(4, 4)
        s_shadow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s_shadow.fill((0, 0, 0, 120))
        pygame.draw.rect(s_shadow, (0, 0, 0, 0), s_shadow.get_rect(), border_radius=15)
        surface.blit(s_shadow, shadow_rect.topleft)

        # Основной градиент кнопки
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        col = (
            self.current_color
            if len(self.current_color) != 4
            else self.current_color[:3]
        )
        for i in range(self.rect.height):
            alpha = 255 - int(100 * i / self.rect.height)
            s.fill(col + (alpha,), (0, i, self.rect.width, 1))
        pygame.draw.rect(s, config.BLACK, s.get_rect(), 3, border_radius=15)
        surface.blit(s, self.rect.topleft)

        text_surf = font.render(self.text, True, self.text_color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def update(self, mouse_pos):
        self.current_color = (
            self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
        )

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
