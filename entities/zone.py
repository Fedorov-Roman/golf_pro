class Zone:
    """Датакласс игровой зоны (заглушка для будущей системы)."""

    def __init__(
        self, type_, pos, radius=0, width=0, height=0, shape="circle", params=None
    ):
        self.type = type_
        self.pos = pos
        self.radius = radius
        self.width = width
        self.height = height
        self.shape = shape
        self.params = params or {}

    def contains(self, point):
        """Проверяет, находится ли точка внутри зоны."""
        dx = point[0] - self.pos[0]
        dy = point[1] - self.pos[1]
        if self.shape == "circle":
            return (dx * dx + dy * dy) <= self.radius * self.radius
        elif self.shape == "rect":
            return (abs(dx) <= self.width / 2) and (abs(dy) <= self.height / 2)
        return False
