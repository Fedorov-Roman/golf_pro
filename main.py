import pygame
import config
from core.game import GolfGame

def main():
    pygame.init()
    info = pygame.display.Info()
    config.SCREEN_WIDTH = info.current_w
    config.SCREEN_HEIGHT = info.current_h
    config.WORLD_WIDTH = info.current_w * 2
    config.WORLD_HEIGHT = info.current_h * 2
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    game = GolfGame(screen)
    game.run()

if __name__ == "__main__":
    main()
    