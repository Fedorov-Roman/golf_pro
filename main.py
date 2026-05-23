import pygame
import sys
import config
from core.game import GolfGame


def main():
    pygame.init()
    # Создаём полноэкранное окно с родным разрешением (автоопределение)
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    # Получаем реальные размеры экрана
    config.SCREEN_WIDTH = screen.get_width()
    config.SCREEN_HEIGHT = screen.get_height()
    # Передаём готовый screen в игру
    game = GolfGame(screen)
    game.run()


if __name__ == "__main__":
    main()
