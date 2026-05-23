class Obstacle:
    __slots__ = ("type", "pos", "radius", "image")

    def __init__(self, type_, pos, radius, image):
        self.type = type_
        self.pos = pos
        self.radius = radius
        self.image = image
