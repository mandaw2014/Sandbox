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
        self.jumppad4 = JumpPad(player, position = (-131, -42, -33), jump_height = 70)
        self.jumppad5 = JumpPad(player, position = (16, -37, -91))
        self.jumppad6 = JumpPad(player, position = (43.5, -53.5, 118))

        self.coin = Coin(player)

        self.pads = [self.jumppad1, self.jumppad2, self.jumppad3, self.jumppad4, self.jumppad5]

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
        if distance(self, self.player) < 10:
            self.player.velocity_y = self.jump_height

class Coin(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "coin.obj",
            texture = "level",
            scale = 10,
            collider = "box",
            **kwargs
        )

        self.player = player
        self.hit = False

        self.prev_y = self.y
        self.y_speed = 0

        self.positions = [
            Vec3(-170, -73, -81), Vec3(-28, 35, 57), Vec3(-21, 2, -39),
            Vec3(-131, -39, -33), Vec3(16, -34, -91), Vec3(43.5, -50, 118)
        ]

        self.random_pos()

    def update(self):
        if distance(self, self.player) < 10 and not self.hit:
            self.hit = True
            self.player.score += 5
            self.player.score_text.text = str(self.player.score)
            self.animate_rotation((0, self.rotation_y + 1000, 0), 0.7, curve = curve.linear)
            invoke(self.fade_out, delay = 0.6)
            invoke(self.random_pos, delay = 5)
            invoke(setattr, self, "hit", False, delay = 5)

        self.rotation_y += 30 * time.dt
        self.y += self.y_speed * time.dt
        if self.y < self.prev_y:
            self.y_speed = 10
        elif self.y > self.prev_y + 2:
            self.y_speed -= 30 * time.dt

    def random_pos(self):
        pos = random.randint(0, len(self.positions) - 1)
        self.position = self.positions[pos]
        self.prev_y = self.y + 1
        self.alpha = 255