import math
import random
import config

class ShotSystem:
    """Система прицеливания и расчёта удара."""
    def __init__(self):
        self.is_aiming = False
        self.aim_start = (0, 0)
        self.aim_current = (0, 0)
        self.aim_accumulated = (0.0, 0.0)

        self.selecting_angle = False
        self.angle_value = 0.0
        self.pending_shoot = None

    def start_aim(self, ball_pos, mouse_pos):
        self.is_aiming = True
        self.aim_start = ball_pos
        self.aim_current = mouse_pos
        self.aim_accumulated = (0.0, 0.0)

    def accumulate_motion(self, rel):
        self.aim_accumulated = (
            self.aim_accumulated[0] + rel[0],
            self.aim_accumulated[1] + rel[1]
        )
        self.aim_current = (
            self.aim_current[0] + rel[0],
            self.aim_current[1] + rel[1]
        )

    def finish_aim(self, club):
        self.is_aiming = False
        acc_x, acc_y = self.aim_accumulated
        dist = math.hypot(acc_x, acc_y)
        if dist > 10:
            direction = (acc_x / dist, acc_y / dist)
            power = min(dist * 1.8, club.max_power)
            self.aim_accumulated = (0.0, 0.0)
            return (direction, power)
        self.aim_accumulated = (0.0, 0.0)
        return None

    def cancel_aim(self):
        self.is_aiming = False
        self.aim_accumulated = (0.0, 0.0)

    def update_angle(self, mouse_world_y, ball_world_y, zoom=1.0):
        """Обновляет значение угла по вертикальному положению мыши в мировых координатах."""
        dy = mouse_world_y - ball_world_y
        world_radius = config.ANGLE_SELECT_RADIUS / zoom
        dy = max(0.0, min(world_radius, dy))
        self.angle_value = (dy / world_radius) * config.MAX_ANGLE

    def start_angle_selection(self, direction, power):
        self.selecting_angle = True
        self.pending_shoot = (direction, power)
        self.angle_value = 0.0

    def confirm_angle(self):
        self.selecting_angle = False
        if self.pending_shoot is not None:
            direction, power = self.pending_shoot
            angle = self.angle_value
            self.pending_shoot = None
            return (direction, power, angle)
        return None

    def calculate_shot(self, direction, power, club, angle_deg):
        power = min(power, club.max_power)
        base_vel = power * 1.0

        if club.accuracy > 0:
            noise = random.uniform(-club.accuracy, club.accuracy) * math.pi / 180
            cos_a, sin_a = math.cos(noise), math.sin(noise)
            dir_x = direction[0] * cos_a - direction[1] * sin_a
            dir_y = direction[0] * sin_a + direction[1] * cos_a
            direction = (dir_x, dir_y)

        theta = math.radians(angle_deg)
        v_horiz = base_vel * math.cos(theta)
        v_vert = base_vel * math.sin(theta)

        return {
            "vel": (direction[0] * v_horiz, direction[1] * v_horiz),
            "vz": v_vert,
            "z": 0.1,
            "spin": (0.0, 0.0)
        }
