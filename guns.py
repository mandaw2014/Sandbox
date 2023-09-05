from ursina import *
from ursina import curve
from trail_renderer import TrailRenderer

from particles import Particles

class Gun(Entity):
    def __init__(self, player, equipped = True, **kwargs):
        super().__init__(
            parent = camera,
            scale = 0.3,
            position = (0.5, -0.75, 1.7),
            **kwargs
        )
        
        self.player = player
        self.map = self.player.map
        self.tip = Entity(parent = self, position = (-0.5, 1.3, 1.5))

        self.pos_x = 0.5
        self.pos_y = -0.75

        # Pivot
        self.pivot = Entity(parent = camera, position = (0.5, -0.75, 1.7))

        # Cooldown
        self.cooldown_t = 0
        self.cooldown_length = 0.3
        self.can_shoot = True
        self.started_shooting = False

        # Damage
        self.damage = 1

        # Spring
        self.spring = Spring()
        self.start_spring = False

        # Camera Shake amount
        self.shake_divider = 70

        # Gun type
        self.gun_type = "pistol"
        self.charged = False
        self.equipped = equipped

        # Audio
        self.gun_sound = Audio("pistol.wav", False)
        self.destroyed_enemy = Audio("destroyed.wav", False)
        self.gun_sound.volume = 0.8
        self.destroyed_enemy.volume = 0.1

    def update(self):
        if self.player.enabled:
            if self.equipped:
                self.cooldown_t += time.dt
                if self.cooldown_t >= self.cooldown_length:
                    self.cooldown_t = 0
                    self.can_shoot = True

                    if held_keys["left mouse"] and not self.started_shooting:
                        if self.gun_type == "minigun":
                            if self.charged:
                                self.shoot()
                        else:
                            self.shoot()

                # Springs
                if self.start_spring:
                    gun_movement = self.spring.update(time.dt)
                    self.spring.shove(Vec3(mouse.x, mouse.y, 0))
                    self.x = gun_movement.x + self.pos_x
                    self.y = gun_movement.y + self.pos_y

            if not self.equipped:
                # Pivot Springs
                pivot_movement = self.spring.update(time.dt)
                self.spring.shove(Vec3(mouse.x, mouse.y, 0))
                self.pivot.x = pivot_movement.x + self.pos_x
                self.pivot.y = pivot_movement.y + self.pos_y

    def shoot(self):
        # Spawn bullet
        if self.equipped:
            if self.gun_type == "pistol":
                Bullet(self, self.tip.world_position)
                
                self.gun_sound.clip = "pistol.wav"
                self.gun_sound.volume = 0.8
                self.gun_sound.play()

            elif self.gun_type == "shotgun":
                for i in range(random.randint(2, 4)):
                    b = Bullet(self, self.tip.world_position, randomness = 10)

                self.gun_sound.clip = "shotgun.wav"
                self.gun_sound.volume = 0.8
                self.gun_sound.play()
            elif self.gun_type == "rifle":
                Bullet(self, self.tip.world_position)

                self.gun_sound.clip = "rifle.wav"
                self.gun_sound.volume = 0.8
                self.gun_sound.play()
            elif self.gun_type == "minigun":
                Bullet(self, self.tip.world_position)

                self.shooting = True
                self.gun_sound.clip = "minigun.wav"
                self.gun_sound.volume = 0.8
                self.gun_sound.play()

            # Animate the gun
            if self.gun_type == "pistol" or self.gun_type == "shotgun":
                self.animate_rotation((-30, 0, 0), duration = 0.1, curve = curve.linear)
                self.animate("z", 1, duration = 0.03, curve = curve.linear)
                self.animate("z", 1.5, 0.2, delay = 0.1, curve = curve.linear)
                self.animate_rotation((-15, 0, 0), 0.2, delay = 0.1, curve = curve.linear)
                self.animate_rotation((0, 0, 0), 0.4, delay = 0.12, curve = curve.linear)
            elif self.gun_type == "rifle":
                self.animate_rotation((-20, 0, 0), duration = 0.1, curve = curve.linear)
                self.animate("z", 1.2, duration = 0.03, curve = curve.linear)
                self.animate("z", 1.5, 0.2, delay = 0.1, curve = curve.linear)
                self.animate_rotation((-10, 0, 0), 0.2, delay = 0.1, curve = curve.linear)
                self.animate_rotation((0, 0, 0), 0.4, delay = 0.12, curve = curve.linear)
            elif self.gun_type == "minigun":
                self.animate_rotation((-10, 0, 0), duration = 0.05, curve = curve.linear)
                self.animate("z", 1, duration = 0.015, curve = curve.linear)
                self.animate("z", 1.5, 0.2, delay = 0.05, curve = curve.linear)
                self.animate_rotation((-5, 0, 0), 0.2, delay = 0.05, curve = curve.linear)
                self.animate_rotation((0, 0, 0), 0.4, delay = 0.06, curve = curve.linear)

            self.can_shoot = False
            
            # Camera Shake
            self.player.shake_camera(0.1, self.shake_divider)

    def equip(self):
        self.equipped = True
        self.on_equipped()

    def input(self, key):
        if key == "left mouse down" and self.can_shoot:
            if self.gun_type == "minigun":
                if self.charged:
                    self.shoot()
                    self.started_shooting = True
                    invoke(setattr, self, "started_shooting", False, delay = self.cooldown_length / 2)
                else:
                    self.barrel.animate("rotation_z", self.barrel.rotation_z + 720, 1)
                    invoke(setattr, self, "charged", True, delay = 1)

                self.player.speed = 2
            else:
                self.shoot()
                self.started_shooting = True
                invoke(setattr, self, "started_shooting", False, delay = self.cooldown_length / 2)

        elif key == "left mouse up":
            if hasattr(self, "shooting"):
                self.shooting = False
            self.charged = False
            self.player.speed = 5

    def on_enable(self):
        self.on_equipped()
        
    def on_equipped(self): 
        self.y = -2
        self.rotation_x = 50
        try:
            self.animate("y", self.pos_y, duration = 0.4, curve = curve.linear)
        except AttributeError:
            self.animate("y", -0.5, duration = 0.4, curve = curve.linear)
        self.animate("rotation_x", 0, duration = 0.4, curve = curve.linear)
        invoke(setattr, self, "start_spring", True, delay = 0.4)

    def on_disable(self):
        self.start_spring = False

class Bullet(Entity):
    def __init__(self, gun, pos, speed = 2000, trail_colour = color.hex("#00baff"), randomness = 0):
        super().__init__(
            model = "bullet.obj",
            texture = "level.png",
            scale = 0.08,
            position = pos
        )

        self.gun = gun
        self.speed = speed
        self.hit_player = False
        self.randomness = Vec3(random.randint(-10, 10) * random.randint(-1, 1), random.randint(-10, 10) * random.randint(-1, 1), random.randint(-10, 10) * random.randint(-1, 1)) * Vec3(randomness)
        self.enemy = None

        self.trail_thickness = 8
        self.trail = TrailRenderer(self.trail_thickness, trail_colour, color.clear, 5, parent = self)

        if hasattr(self.gun, "tip"):
            self.rotation = camera.world_rotation
            self.is_player = True
            self.no_point = False
        else:
            self.world_rotation = self.gun.world_rotation
            self.is_player = False

        if self.is_player:
            if mouse.hovered_entity:
                if mouse.hovered_entity != self.gun.player.map:
                    self.hovered_point = mouse.hovered_entity
                    self.animate("position", Vec3(self.hovered_point.world_position) + (self.forward * 10000) + self.randomness, distance(self.hovered_point.world_position + (self.forward * 10000), self.gun.player) / 150, curve = curve.linear)
                else:
                    self.hovered_point = mouse.world_point
                    self.animate("position", Vec3(self.hovered_point) + self.randomness + (self.forward * 10000), distance(self.hovered_point + (self.forward * 10000), self.gun.player) / 150, curve = curve.linear)
                
            else:
                self.animate("position", self.world_position + (self.forward * 10000) + self.randomness, 5, curve = curve.linear)
                self.no_point = True
            
            destroy(self, 2)

    def update(self):   
        if self.is_player:
            if not self.no_point:
                if self.hovered_point != self.gun.player.map and not isinstance(self.hovered_point, LVector3f):
                    if distance(self, self.hovered_point) < 3 and self.hovered_point != self.gun.player:
                        for i in range(2):
                            p = Particles(self.hovered_point.world_position, Vec3(random.random(), random.randrange(-10, 10, 1) / 10, random.random()), spray_amount = 10, model = "particles")
                            
                        self.hovered_point.health -= self.gun.damage
                        self.hovered_point.texture = "hit.png"
                        invoke(setattr, self.hovered_point, "texture", "level", delay = 0.1)
                        if self.hovered_point.health <= 0:
                            for i in range(6):
                                p = Particles(self.hovered_point.world_position, Vec3(random.random(), random.randrange(-10, 10, 1) / 10, random.random()), spray_amount = 10, model = "particles", texture = "destroyed")
                            self.hovered_point.reset_pos()
                            self.hovered_point.health = 2
                            self.gun.player.shot_enemy()
                            self.gun.destroyed_enemy.play() 
                        
                        destroy(self)
                else:
                    if self.gun.gun_type != "shotgun":
                        if distance(self, self.hovered_point) < 3 and self.hovered_point != self.gun.player:
                            for i in range(2):
                                p = Particles(self.hovered_point - (self.forward * 10), Vec3(random.random(), random.random(), random.random()), 30, model = "particles")

                            destroy(self)
                    else:
                        level_ray = raycast(self.world_position, self.forward, distance = 3, traverse_target = self.gun.player.map, ignore = [self, self.gun, self.gun.player])
                        if level_ray.hit:
                            for i in range(2):
                                p = Particles(self.hovered_point - (self.forward * 10), Vec3(random.random(), random.random(), random.random()), 30, model = "particles")

                            destroy(self)
        else:
            self.position += self.forward * self.speed * time.dt

            level_ray = raycast(self.world_position, self.forward, distance = 3, traverse_target = self.gun.player.map, ignore = [self, self.gun])
            if distance(self, self.gun.player) <= 2:
                if not self.hit_player:
                    self.gun.player.health -= self.enemy.damage
                    self.gun.player.healthbar.value = self.gun.player.health
                    self.hit_player = True
                destroy(self)
            if level_ray.hit:
                destroy(self)
            destroy(self, delay = 2)

class Rocket(Entity):
    def __init__(self, gun, pos, speed = 100, trail_colour = color.hex("#00baff"), randomness = 0, cooldown = 3):
        super().__init__(
            model = "rocket.obj",
            texture = "level.png",
            position = pos,
            parent = gun
        )

        self.gun = gun
        self.speed = speed
        self.randomness = Vec3(random.randint(-10, 10) * random.randint(-1, 1), random.randint(-10, 10) * random.randint(-1, 1), random.randint(-10, 10) * random.randint(-1, 1)) * Vec3(randomness)
        self.pos = pos
        self.trail_colour = trail_colour
        self.no_point = False
        self.cooldown = cooldown

        self.fired = False
        self.gun.ready = True

    def fire(self):
        self.fired = True
        self.parent = scene
        self.gun.ready = False
        self.position = self.gun.world_position
        self.rotation = camera.world_rotation
        
        self.trail_thickness = 8
        self.trail = TrailRenderer(self.trail_thickness, self.trail_colour, color.clear, 5, parent = self)
    
        if mouse.hovered_entity:
            if mouse.hovered_entity != self.gun.player.map:
                self.hovered_point = mouse.hovered_entity
                self.animate("position", Vec3(self.hovered_point.world_position) + (self.forward) + self.randomness, distance(self.hovered_point.world_position + (self.forward), self.gun.player) / 150, curve = curve.linear)
            else:
                self.hovered_point = mouse.world_point
                self.animate("position", Vec3(self.hovered_point) + self.randomness + (self.forward), distance(self.hovered_point + (self.forward), self.gun.player) / 150, curve = curve.linear)
            self.no_point = False
        else:
            self.animate("position", self.world_position + (self.forward * 400) + self.randomness, 1.9, curve = curve.linear)
            self.no_point = True

    def update(self): 
        if self.fired and not self.no_point:
            if self.hovered_point != self.gun.player.map and not isinstance(self.hovered_point, LVector3f):
                if distance(self, self.hovered_point) < 5 and self.hovered_point != self.gun.player:
                    for i in range(2):
                        p = Particles(self.hovered_point.world_position, Vec3(random.random(), random.randrange(-10, 10, 1) / 10, random.random()), spray_amount = 10, model = "particles")
                    
                    for enemy in self.gun.player.enemies:
                        if distance(self, enemy) < 10:
                            enemy.health -= (self.gun.damage - distance(self, enemy))
                            enemy.texture = "hit.png"
                            invoke(setattr, enemy, "texture", "level", delay = 0.1)
                            if enemy.health <= 0:
                                for i in range(6):
                                    p = Particles(enemy.world_position, Vec3(random.random(), random.randrange(-10, 10, 1) / 10, random.random()), spray_amount = 10, model = "particles", texture = "destroyed")
                                enemy.reset_pos()
                                enemy.health = 2
                                self.gun.player.shot_enemy()
                                self.gun.destroyed_enemy.play() 
                    
                    destroy(self)
            else:
                level_ray = raycast(self.world_position, self.forward, distance = 3, traverse_target = self.gun.player.map, ignore = [self, self.gun, self.gun.player])
                if level_ray.hit:
                    for i in range(10):
                        p = Particles(self.hovered_point - (self.forward * 10), Vec3(random.random(), random.random(), random.random()), 30, model = "particles", texture = "jetpack")

                    destroy(self)

class Pistol(Gun):
    def __init__(self, player, equipped = True, **kwargs):
        super().__init__(
            model = "pistol.obj",
            texture = "level.png",
            player = player,
            equipped = equipped,
            **kwargs
        )

        self.gun_type = "pistol"
        self.equip()

class Shotgun(Gun):
    def __init__(self, player, equipped = False, **kwargs):
        super().__init__(
            model = "shotgun.obj",
            texture = "level.png",
            player = player,
            equipped = equipped,
            **kwargs
        )

        self.gun_type = "shotgun"
        self.tip.z = 2

        self.pos_x = 0.6
        self.pos_y = -0.5

        self.damage = 1

        self.shake_divider = 40
        self.cooldown_length = 0.8

class Rifle(Gun):
    def __init__(self, player, equipped = True, **kwargs):
        super().__init__(
            model = "rifle.obj",
            texture = "level.png",
            player = player,
            equipped = equipped,
            **kwargs
        )

        self.gun_type = "rifle"
        self.tip.z = 8
        self.tip.y = 0

        self.pos_x = 0.6
        self.pos_y = -0.5

        self.damage = 0.8

        self.shake_divider = 80
        self.cooldown_length = 0.2
        self.equip()

class MiniGun(Gun):
    def __init__(self, player, equipped = False, **kwargs):
        super().__init__(
            model = "minigun.obj",
            texture = "level.png",
            player = player,
            equipped = equipped,
            **kwargs
        )

        self.barrel = Entity(model = "minigun-barrel", texture = "level", parent = self)
        self.shooting = False

        self.gun_type = "minigun"
        self.tip.z = 7
        self.tip.y = 0

        self.pos_x = 0.9
        self.pos_y = -1.2

        self.damage = 0.5

        self.shake_divider = 70
        self.cooldown_length = 0.1

    def update(self):
        if self.shooting:
            self.barrel.rotation_z += 400 * time.dt
        return super().update()
    
class RocketLauncher(Gun):
    def __init__(self, player, equipped = False, **kwargs):
        super().__init__(
            model = "rocket-launcher.obj",
            texture = "level.png",
            player = player,
            equipped = equipped,
            **kwargs
        )

        self.gun_type = "rocket launcher"
        self.tip.z = 8
        self.tip.y = 0

        self.pos_x = 0.6
        self.pos_y = -0.5

        self.damage = 10
        self.ready = True

        self.shake_divider = 20
        self.cooldown_length = 5

        self.rocket = Rocket(self, (0, 0, 0))

    def input(self, key):
        if key == "left mouse down" and self.ready:
            self.rocket.fire()
            self.animate_rotation((-40, 0, 0), duration = 0.1, curve = curve.linear)
            self.animate("z", 0.5, duration = 0.1, curve = curve.linear)
            self.animate("z", 1.5, 0.2, delay = 0.1, curve = curve.linear)
            self.animate_rotation((-5, 0, 0), 0.5, delay = 0.15, curve = curve.linear)
            self.animate_rotation((0, 0, 0), 0.6, delay = 0.5, curve = curve.linear)
            
            self.player.shake_camera(0.1, self.shake_divider)
            invoke(self.reload, delay = 3)

            self.gun_sound.clip = "rocket_launcher.wav"
            self.gun_sound.play()

    def reload(self):
        self.rocket = Rocket(self, (0, 0, 0))

class Spring:
    def __init__(self, mass = 5, force = 50, damping = 4, speed = 4):
        self.target = Vec3()
        self.position = Vec3()
        self.velocity = Vec3()

        self.iterations = 8

        self.mass = mass
        self.force = force
        self.damping = damping
        self.speed = speed

    def shove(self, force):
        x, y, z = force.x, force.y, force.z

        if x != x:
            x = 0
        if y != y:
            y = 0
        if z != z:
            z = 0

        self.velocity = self.velocity + Vec3(x, y, z)

    def update(self, dt):
        scaledDeltaTime = min(dt,1) * self.speed / self.iterations

        for i in range(self.iterations):
            iterationForce = self.target - self.position
            acceleration = (iterationForce * self.force) / self.mass

            acceleration = acceleration - self.velocity * self.damping

            self.velocity = self.velocity + acceleration * scaledDeltaTime
            self.position = self.position + self.velocity * scaledDeltaTime

        return self.position