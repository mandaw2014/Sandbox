from ursina import *

class SkyLevel(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "skylevel.obj", 
            texture = "level.png", 
            collider = "mesh",
            **kwargs
        )

        self.jumppad1 = JumpPad(player, jump_height = 80, position = (-28, 4, -61), rotation_y = -6, level = self)
        self.jumppad2 = JumpPad(player, jump_height = 30, position = (6.5, 4, 53), rotation_y = 30, level = self)
        self.jumppad3 = JumpPad(player, jump_height = 70, position = (31, 14, 37), rotation_y = 30, level = self)

class DesertLevel(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "desertlevel.obj", 
            texture = "level.png", 
            collider = "mesh",
            **kwargs
        )

class JumpPad(Entity):
    def __init__(self, player, jump_height = 100, position = (0, 0, 0), level = None, **kwargs):
        super().__init__(
            model = "jumppad.obj",
            texture = "level",
            position = position,
            scale = 6,
            **kwargs
        )

        self.player = player
        self.jump_height = jump_height
        self.level = level

    def update(self):
        if distance(self, self.player) < 10:
            self.player.velocity_y = self.jump_height

    def input(self, key):
        if self.level.enabled:
            self.enable()
        elif not self.level.enabled:
            self.disable()