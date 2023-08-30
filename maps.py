from ursina import *

class FloatingIslands(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "floatingislands.obj", 
            texture = "level.png", 
            collider = "mesh",
            **kwargs
        )

        self.jumppad1 = JumpPad(player, jump_height = 80, position = (-28, 4, -61), rotation_y = -6, level = self)
        self.jumppad2 = JumpPad(player, jump_height = 30, position = (6.5, 4, 53), rotation_y = 30, level = self)
        self.jumppad3 = JumpPad(player, jump_height = 70, position = (31, 14, 37), rotation_y = 30, level = self)

class DesertedSands(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "desertedsands.obj", 
            texture = "level.png", 
            collider = "mesh",
            **kwargs
        )

class MountainousValley(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "mountainous_valley.obj", 
            texture = "level.png", 
            collider = "mesh",
            **kwargs
        )

        self.jumppad1 = JumpPad(player, jump_height = 80, position = (-7, 15, -49), level = self, rotation_y = -40, scale = 5, visible = False)
        self.jumppad2 = JumpPad(player, jump_height = 80, position = (41, 22.5, -18), rotation_y = -20, scale = 5, level = self, visible = False)
        self.jumppad3 = JumpPad(player, jump_height = 80, position = (-26, 67, 3), rotation_y = 40, scale = 4, level = self, visible = False)
        self.jumppad4 = JumpPad(player, jump_height = 80, position = (-5, -12, 57), rotation_y = 20, scale = 5, level = self, visible = False)
        self.jumppad5 = JumpPad(player, jump_height = 80, position = (56, -5.3, 2), rotation_y = 0, level = self, visible = False)

        self.player = player

    def update(self):
        if self.player.y <= -51:
            self.player.position = (-5, 105, -10)
            self.player.rotation_y = -270
            self.player.velocity_x = 0
            self.player.velocity_y = 0
            self.player.velocity_z = 0
            self.player.health -= 5
            self.player.healthbar.value = self.player.health

class JumpPad(Entity):
    def __init__(self, player, jump_height = 100, position = (0, 0, 0), level = None, scale = 6, **kwargs):
        super().__init__(
            model = "jumppad.obj",
            texture = "level",
            position = position,
            scale = scale,
            **kwargs
        )

        self.player = player
        self.jump_height = jump_height
        self.level = level

    def update(self):
        if self.visible and distance(self, self.player) < 10:
            self.player.velocity_y = self.jump_height

    def input(self, key):
        if self.level.enabled:
            self.visible = True
        elif not self.level.enabled:
            self.visible = False