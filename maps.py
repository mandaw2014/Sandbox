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

        self.jumppad1 = JumpPad(player, jump_height = 80, position = (2, -24, 0), level = self, rotation_y = -40, scale = 5, model = None)
        self.jumppad2 = JumpPad(player, jump_height = 80, position = (0, 45, 3), level = self, rotation_y = -40, scale = 5, model = None)

class MountainousValley(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "mountainous_valley.obj", 
            texture = "level.png", 
            collider = "mesh",
            scale = 3,
            y = -200,
            **kwargs
        )

        self.jumppad1 = JumpPad(player, jump_height = 100, position = (-6, 26, -44), level = self, rotation_y = -40, scale = 5, model = None)
        self.jumppad2 = JumpPad(player, jump_height = 100, position = (-89, 2, 45), rotation_y = -20, scale = 5, level = self, model = None)
        self.jumppad3 = JumpPad(player, jump_height = 100, position = (58, 39, -1), rotation_y = 40, scale = 4, level = self, model = None)
        self.jumppad4 = JumpPad(player, jump_height = 100, position = (81, -5, 29), rotation_y = 20, scale = 5, level = self, model = None)
        self.jumppad5 = JumpPad(player, jump_height = 100, position = (-49, 115, 27), rotation_y = 0, level = self, model = None)
        self.jumppad6 = JumpPad(player, jump_height = 100, position = (-13, -19, 121), rotation_y = 0, level = self, model = None)

        self.player = player

    def update(self):
        if self.player.y <= -90:
            self.player.position = (-5, 200, -10)
            self.player.rotation_y = -270
            self.player.velocity_x = 0
            self.player.velocity_y = 0
            self.player.velocity_z = 0
            self.player.health -= 5
            self.player.healthbar.value = self.player.health

class JumpPad(Entity):
    def __init__(self, player, jump_height = 100, model = "jumppad.obj", position = (0, 0, 0), level = None, scale = 6, **kwargs):
        super().__init__(
            model = model,
            texture = "level",
            position = position,
            scale = scale,
            **kwargs
        )

        self.player = player
        self.jump_height = jump_height
        self.level = level

        if not self.show:
            self.visible = False

    def update(self):
        if self.visible and distance(self, self.player) < 10:
            self.player.velocity_y = self.jump_height

    def input(self, key):
        if self.level.enabled:
            self.visible = True
        elif not self.level.enabled:
            self.visible = False