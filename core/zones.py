class ZoneManager:
    """Менеджер игровых зон (пока заглушка)."""

    def __init__(self):
        self.zones = []

    def load_zones(self, zones_list):
        self.zones = list(zones_list) if zones_list else []

    def apply_physics(self, ball, dt, field_type="forest"):
        """Заглушка применения модификаторов зон."""
        pass

    def get_zone_at(self, pos):
        """Возвращает первую зону, содержащую точку, или None."""
        for z in self.zones:
            if z.contains(pos):
                return z
        return None
