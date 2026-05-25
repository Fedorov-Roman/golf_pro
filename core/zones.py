# core/zones.py (полный файл)
import config
import math


class ZoneManager:
    def __init__(self):
        self.zones = []
        self.obstacles = []

    def load_zones(self, zones_list, obstacles_list=None):
        self.zones = list(zones_list) if zones_list else []
        self.obstacles = list(obstacles_list) if obstacles_list else []

    def get_zone_at(self, pos):
        for z in self.zones:
            if z.contains(pos):
                return z
        for obs in self.obstacles:
            if obs["type"] == "sand":
                dist = math.hypot(pos[0] - obs["pos"][0], pos[1] - obs["pos"][1])
                if dist < obs["radius"]:
                    return _BunkerZone(obs)
        return None

    def get_zone_type_at(self, pos):
        zone = self.get_zone_at(pos)
        return zone.type if zone else None

    def get_shot_modifier(self, ball):
        zone = self.get_zone_at(ball.pos)
        if zone is None:
            return 1.0, 0
        if zone.type == "rough":
            return config.ROUGH_POWER_MULT, 0
        elif zone.type == "bunker":
            return config.BUNKER_POWER_MULT, config.BUNKER_MIN_ANGLE
        return 1.0, 0

    def apply_physics(self, ball, dt, field_type="forest"):
        # Трение rough теперь обрабатывается в physics.py через get_zone_type_at,
        # здесь больше не нужно изменять скорость.
        pass


class _BunkerZone:
    def __init__(self, obs):
        self.type = "bunker"
        self.pos = obs["pos"]
        self.radius = obs["radius"]
