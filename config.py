import pygame

# Размеры экрана (задаются в main.py)
SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0
FPS = 60

# Размеры игрового мира (больше экрана)
WORLD_WIDTH = 0
WORLD_HEIGHT = 0

# Зум
MIN_ZOOM = 0.5
MAX_ZOOM = 2.0
ZOOM_STEP = 0.1

# Цвета (без изменений)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (40, 40, 40)
RED = (220, 50, 50)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
BLUE = (30, 144, 255)
LIGHT_BLUE = (173, 216, 230)
BROWN = (139, 69, 19)
SAND_COLOR = (238, 203, 173)
SNOW_WHITE = (245, 245, 245)
WATER_BLUE = (65, 105, 225)
WOOD = (101, 67, 33)
ICE_COLOR = (200, 230, 255)

# Физика (без изменений)
STOP_THRESHOLD = 1.0
WIND_THRESHOLD = 45.0
BALL_RADIUS = 9
BASE_FRICTION = 50.0
FAIRWAY_FRICTION = 35.0
MARGIN = 20
SAND_FRICTION_MULT = 5.0
MAX_HOLE_SPEED = 100.0
ICE_FRICTION_MULT = 0.0
WATER_OUTLINE = 3

# Фервей
FAIRWAY_WIDTH = 80
FAIRWAY_SEGMENTS = 100
FAIRWAY_MARGIN = 15
A_STAR_CELL_SIZE = 40
FAIRWAY_SMOOTH_STEP = 10
FAIRWAY_SMOOTH_PASSES = 4

# Зоны
TEE_RADIUS = FAIRWAY_WIDTH // 2 + 10       # 50
GREEN_RADIUS = TEE_RADIUS * 3              # 150

# Параболическая физика
GRAVITY = 600.0
MIN_ANGLE = 0
MAX_ANGLE = 70
ANGLE_SELECT_RADIUS = 40

# Клюшки (без изменений)
class Club:
    def __init__(self, name, max_power, accuracy, color, icon_color):
        self.name = name
        self.max_power = max_power
        self.accuracy = accuracy
        self.color = color
        self.icon_color = icon_color

CLUBS = [
    Club("Драйвер", 600, 5.0, (200, 100, 50), (160, 82, 45)),
    Club("Вуд",     500, 3.5, (160, 82, 45), (139, 69, 19)),
    Club("Айрон",   400, 2.5, (150, 150, 150), (105, 105, 105)),
    Club("Ведж",    250, 1.2, (200, 200, 100), (184, 134, 11)),
    Club("Паттер",  150, 0.0, (180, 180, 180), (128, 128, 128))
]

FIELD_PRESETS = {
    "forest": {"bg": (34, 139, 34), "tree": (0, 100, 0), "sand": (238, 203, 173), "water": BLUE},
    "desert": {"bg": (238, 203, 173), "tree": (139, 69, 19), "sand": (244, 164, 96), "water": LIGHT_BLUE},
    "snow":   {"bg": (245, 245, 245), "tree": (169, 169, 169), "sand": (220, 220, 220), "water": (135, 206, 250)}
}

WEATHER_PARAMS = {
    "sunny": {"wind_range": (0, 0), "rain_mult": 1.0},
    "rain":  {"wind_range": (15, 35), "rain_mult": 2.5},
    "windy": {"wind_range": (50, 90), "rain_mult": 1.0},
}

PLAYER_COLORS = [
    (255, 60, 60),
    (60, 120, 255),
    (60, 200, 60),
    (255, 215, 0),
    (200, 100, 255)
]

MENU_GRADIENT_TOP = (25, 60, 25)
MENU_GRADIENT_BOTTOM = (5, 15, 5)

# Будущие параметры (не используются)
MAX_SPIN_FORCE = 50.0
MAGNUS_COEFFICIENT = 0.1
CAMERA_LERP_SPEED = 5.0
CAMERA_HIT_DISTANCE = 200
