from ursina import *
from particles import Particles
from guns import Bullet

class Enemy(Entity):
    def __init__(self, player, move_speed = 20, position = (0, 0, 0), **kwargs):
        super().__init__(
            model = "enemy.obj",
            texture = "level.png",
            position = position,
            collider = "box",
            **kwargs
        )

        self.player = player
        self.move_speed = move_speed
        self.health = 2
        self.damage = 1

        # Pivots
        self.thruster1 = Entity(parent = self, position = (-0.4, -2, 0))
        self.thruster2 = Entity(parent = self, position = (0.4, -2, 0))

        self.barrel = Entity()

        # Shooting
        self.cooldown_t = 0
        self.cooldown_length = 2

        # Particles
        self.particle_t = 0
        self.particle_amount = 0.4

        self.random = Vec3(random.randrange(-10, 10), random.randrange(0, 3), random.randrange(-10, 10))

        # Audio
        self.gun_sound = Audio("pistol.wav", False)
        self.gun_sound.volume = 0.05

    def update(self):
        if distance(self, self.player) > 20:
            self.position += ((self.player.position + self.random) - self.position).normalized() * self.move_speed * time.dt

        self.look_at(self.player)
        self.rotation_z = 0

        self.barrel.position = self.position + (0, 1, 0) + self.forward
        self.barrel.rotation = self.world_rotation

        # Shooting
        if distance_xz(self, self.player) < 100:
            self.cooldown_t += time.dt
            if self.cooldown_t >= self.cooldown_length:
                self.cooldown_t = 0
                self.cooldown_length = random.uniform(1.5, 3)
                Bullet(self, self.barrel.world_position, 700, color.orange).enemy = self  
                if distance_xz(self, self.player) < 40:
                    self.gun_sound.play()  

        # Particles
        self.particle_t += time.dt
        if self.particle_t >= self.particle_amount:
            self.particle_t = 0
            self.particles1 = Particles(self.thruster1.world_position, Vec3(random.random(), -random.random(), random.random()), 10, texture = "jetpack")
            self.particles2 = Particles(self.thruster2.world_position, Vec3(random.random(), -random.random(), random.random()), 10, texture = "jetpack")

    def reset_pos(self):
        self.position = Vec3(random.randint(-100, 300), random.randint(0, 50), random.randint(-100, 300))

class BigEnemy(Enemy):
    def __init__(self, player, move_speed = 10, position = (0, 0, 0), **kwargs):
        super().__init__(
            player, move_speed, position, **kwargs
        )

        self.model = "bigenemy"
        self.cooldown_length = 3
        self.damage = 2
        self.health = 4