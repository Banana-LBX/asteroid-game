import pyray as pr

class Entity:
    def __init__(self):
        self.position = pr.Vector2(0, 0)
        self.speed = pr.Vector2(0, 0)
        self.heading = 0.00
        self.acceleration = 0.00
        self.active = False
        self.type = 0
