class Camera:
    """Камера с различными режимами. Сейчас только тождественное преобразование."""

    CAM_HIT = "hit"
    CAM_FLIGHT = "flight"
    CAM_ROLL = "roll"
    CAM_GREEN = "green"
    CAM_MAP = "map"

    def __init__(self, screen_w, screen_h):
        self.mode = self.CAM_HIT
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.zoom = 1.0
        self.target_pos = None

    def update(self, dt, target_pos=None):
        """Заглушка плавного перемещения."""
        self.target_pos = target_pos

    def world_to_screen(self, pos):
        """Пока возвращает координаты без изменений."""
        if self.mode == self.CAM_HIT:
            return pos
        # Будущая логика
        return pos

    def screen_to_world(self, pos):
        return pos
