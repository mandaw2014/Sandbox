from ursina import *
from ursina import curve

class Particles(Entity):
    def __init__(self, position, direction = Vec3(random.random(), random.random(), random.random()), spray_amount = 30, **kwargs):
        super().__init__(
            model = "particle.obj",
            texture = "particle.png",
            scale = 0.2,
            position = position, 
            rotation_y = random.random() * 360
        )
        
        self.direction = direction
        self.spray_amount = spray_amount
        self.prev_spray_amount = self.spray_amount

        self.destroy(1)

        for key, value in kwargs.items():
            setattr(self, key ,value)

    def update(self):
        self.position += self.direction * self.spray_amount * time.dt
        self.spray_amount -= self.prev_spray_amount * time.dt

    def destroy(self, delay = 1):
        self.fade_out(duration = 0.2, delay = 0.7, curve = curve.linear)
        destroy(self, delay)
        del self