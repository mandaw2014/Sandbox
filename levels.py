from ursina import *

class FlatLevel(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "flatlevel.obj", 
            texture = "level.png",
            scale = (10, 10, 10), 
            collider = "mesh",
            **kwargs
        )

        self.jumppad1 = JumpPad(player, position = (-170, -76.2, -81))
        self.jumppad2 = JumpPad(player, position = (-28, 32, 57))
        self.jumppad3 = JumpPad(player, position = (-21, -1, -39))

        self.pads = [self.jumppad1, self.jumppad2, self.jumppad3]

    def on_enable(self):
        if hasattr(self, "pads"):
            for pad in self.pads:
                pad.enable()
        
    def on_disable(self):
        if hasattr(self, "pads"):
            for pad in self.pads:
                pad.disable()

class RopeLevel(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "ropelevel.obj", 
            texture = "level.png",
            scale = (30, 30, 30), 
            collider = "mesh",
            **kwargs
        )

class JumpPad(Entity):
    def __init__(self, player, jump_height = 100, position = (0, 0, 0), **kwargs):
        super().__init__(
            model = "jumppad.obj",
            texture = "level",
            world_position = position,
            scale = 6,
            collider = "box",
            **kwargs
        )

        self.player = player
        self.jump_height = jump_height

    def update(self):
        jump_ray = boxcast(self.world_position, (0, 1, 0), distance = 5, traverse_target = self.player, ignore = [self, ], thickness = (15, 5))
        if jump_ray.hit:
            self.player.velocity_y = self.jump_height