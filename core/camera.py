import config

class Camera:
    """Камера с зумом и панорамированием для большого игрового мира."""
    def __init__(self, world_w, world_h, screen_w, screen_h):
        self.world_w = world_w
        self.world_h = world_h
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.pos = [world_w / 2, world_h / 2]  # центр камеры в мировых координатах
        self.zoom = 1.0

    def world_to_screen(self, world_pos):
        """Преобразует мировые координаты в экранные с учётом зума и позиции камеры."""
        x = (world_pos[0] - self.pos[0]) * self.zoom + self.screen_w / 2
        y = (world_pos[1] - self.pos[1]) * self.zoom + self.screen_h / 2
        return (int(x), int(y))

    def screen_to_world(self, screen_pos):
        """Преобразует экранные координаты в мировые."""
        x = (screen_pos[0] - self.screen_w / 2) / self.zoom + self.pos[0]
        y = (screen_pos[1] - self.screen_h / 2) / self.zoom + self.pos[1]
        return (x, y)

    def move(self, dx, dy):
        """Сдвиг камеры в мировых координатах (с учётом текущего зума)."""
        self.pos[0] -= dx / self.zoom
        self.pos[1] -= dy / self.zoom
        self._clamp()

    def zoom_in(self):
        self.zoom = min(config.MAX_ZOOM, self.zoom + config.ZOOM_STEP)
        self._clamp()

    def zoom_out(self):
        self.zoom = max(config.MIN_ZOOM, self.zoom - config.ZOOM_STEP)
        self._clamp()

    def _clamp(self):
        """Ограничивает камеру так, чтобы не выходить за границы мира."""
        half_w = self.screen_w / (2 * self.zoom)
        half_h = self.screen_h / (2 * self.zoom)
        self.pos[0] = max(half_w, min(self.world_w - half_w, self.pos[0]))
        self.pos[1] = max(half_h, min(self.world_h - half_h, self.pos[1]))

    def follow(self, target_world, dt):
        """Плавное следование за целевой точкой (пока просто центрируем)."""
        self.pos[0] = target_world[0]
        self.pos[1] = target_world[1]
        self._clamp()
        