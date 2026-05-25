class Ball:
    __slots__ = (
        "pos",
        "vel",
        "moving",
        "in_hole",
        "visible",
        "player_index",
        "fast_warned",
        "z",
        "vz",
        "in_flight",
        "last_pos",
        "spin_force",
        "trail",
    )

    def __init__(self, player_index, start_pos):
        self.pos = list(start_pos)
        self.vel = [0.0, 0.0]
        self.moving = False
        self.in_hole = False
        self.visible = False
        self.player_index = player_index
        self.fast_warned = False
        self.z = 0.0
        self.vz = 0.0
        self.in_flight = False
        self.last_pos = list(start_pos)
        self.spin_force = [0.0, 0.0]
        self.trail = []

    def stop(self):
        self.vel = [0.0, 0.0]
        self.moving = False

    def land(self):
        self.z = 0.0
        self.vz = 0.0
        self.in_flight = False
        self.moving = True
