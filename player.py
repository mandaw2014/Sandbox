from ursina import *
from ursina import curve

from ursina.prefabs.trail_renderer import TrailRenderer
from ursina.prefabs.health_bar import HealthBar

from particles import Particles

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)

class Player(Entity):
    def __init__(self, position, level, speed = 5, jump_height = 14):
        super().__init__(
            model = "cube", 
            position = position,
            scale = (1.3, 1, 1.3), 
            visible_self = False,
            collider = "box"
        )

        # Camera
        mouse.locked = True
        camera.parent = self
        camera.position = (0, 2, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 90

        # Crosshair
        self.crosshair = Entity(model = "quad", color = color.black, parent = camera, rotation_z = 45, position = (0, 0, 1), scale = 1, z = 100, always_on_top = True)

        # Player values
        self.speed = speed
        self.jump_count = 0
        self.jump_height = jump_height
        self.jumping = False
        self.can_move = True
        self.grounded = False

        # Velocity
        self.velocity = (0, 0, 0)
        self.velocity_x = self.velocity[0]
        self.velocity_y = self.velocity[1]
        self.velocity_z = self.velocity[2]

        # Movement
        self.movementX = 0
        self.movementZ = 0

        self.mouse_sensitivity = 80

        # Level
        self.level = level

        # Gun
        self.gun = Gun(self)
        self.spring = Spring()

        # Rope
        self.rope_pivot = Entity()
        self.rope = Entity(model = Mesh(vertices = [self.world_position, self.rope_pivot.world_position], mode = "line", thickness = 15, colors = [color.hex("#ff8b00")]), texture = "rope.png", enabled = False)
        self.can_rope = False
        self.rope_length = 100
        self.max_rope_length = False
        self.below_rope = False

        # Enemies
        self.enemies = []

        # Health
        self.healthbar = HealthBar(10, bar_color = color.hex("#50acff"), roundness = 0, y = window.bottom_left[1] + 0.1, scale_y = 0.03, scale_x = 0.3)
        self.healthbar.text_entity.disable()
        self.health = 10
        self.ded_text = Text("ded", color = color.black, origin = 0, enabled = False)

    def jump(self):
        self.jumping = True
        self.velocity_y = self.jump_height
        self.jump_count += 1

    def update(self):
        movementY = self.velocity_y * time.dt

        direction = (0, sign(movementY), 0)

        # Main raycast for collision
        y_ray = raycast(origin = self.world_position, direction = self.down, traverse_target = self.level, ignore = [self, ])
            
        if y_ray.distance <= self.scale_y * 1.5 + abs(movementY):
            if not self.grounded:
                self.velocity_y = 0
                self.grounded = True
            # Check if hitting a wall or steep slope
            if y_ray.world_normal.y > 0.7 and y_ray.world_point.y - self.world_y < 0.5:
                # Set the y value to the ground's y value
                if not held_keys["space"]:
                    self.y = y_ray.world_point.y + 1.4
                self.jump_count = 0
                self.jumping = False
        else:
            if not self.can_rope:
                self.velocity_y -= 40 * time.dt
                self.grounded = False

        self.y += movementY * 50 * time.dt

        # Rope
        if self.can_rope:
            if held_keys["right mouse"]:
                if distance(self.position, self.rope_pivot.position) > 5:
                    if distance(self.position, self.rope_pivot.position) < self.rope_length:
                        self.position += ((self.rope_pivot.position - self.position).normalized() * 20 * time.dt)
                        self.velocity_z += 2 * time.dt  
                    self.rope.model.vertices.pop(0)
                    self.rope.model.vertices = [self.position + (0, 1, 0) + (self.forward * 2) + self.left, self.rope_pivot.world_position]
                    self.rope.model.generate()
                    self.rope.enable()
                    if self.y < self.rope_pivot.y:
                        self.velocity_y += 40 * time.dt
                    else:
                        self.velocity_y -= 60 * time.dt

                    if (self.rope_pivot.y - self.y) > self.rope_length:
                        self.below_rope = True
                        invoke(setattr, self, "below_rope", False, delay = 5)

                    if self.below_rope:
                        self.velocity_y += 50 * time.dt
                else:
                    self.rope.disable()
                if distance(self.position, self.rope_pivot.position) > self.rope_length:
                    self.max_rope_length = True
                    invoke(setattr, self, "max_rope_length", False, delay = 2)
                if self.max_rope_length:
                    self.position += ((self.rope_pivot.position - self.position).normalized() * 25 * time.dt)
                    self.velocity_z -= 5 * time.dt
                    self.velocity_y -= 80 * time.dt

        # Velocity / Momentum
        if held_keys["w"]:
            self.velocity_z += 10 * time.dt if y_ray.distance < 5 and not self.can_rope else 5 * time.dt
        else:
            self.velocity_z = lerp(self.velocity_z, 0 if y_ray.distance < 5 else 1, time.dt * 2)
        if held_keys["a"]:
            self.velocity_x += 10 * time.dt if y_ray.distance < 5 and not self.can_rope else 5 * time.dt
        else:
            self.velocity_x = lerp(self.velocity_x, 0 if y_ray.distance < 5 else 1, time.dt * 2)
        if held_keys["s"]:
            self.velocity_z -= 10 * time.dt if y_ray.distance < 5 and not self.can_rope else 5 * time.dt
        else:
            self.velocity_z = lerp(self.velocity_z, 0 if y_ray.distance < 5 else 1, time.dt * 2)
        if held_keys["d"]:
            self.velocity_x -= 10 * time.dt if y_ray.distance < 5 and not self.can_rope else 5 * time.dt
        else:
            self.velocity_x = lerp(self.velocity_x, 0 if y_ray.distance < 5 else -1, time.dt * 2)

        # Movement
        if y_ray.distance <= 5 or self.can_rope:
            self.movementX = (self.forward[0] * self.velocity_z + 
                self.left[0] * self.velocity_x + 
                self.back[0] * -self.velocity_z + 
                self.right[0] * -self.velocity_x) * self.speed * time.dt

            self.movementZ = (self.forward[2] * self.velocity_z + 
                self.left[2] * self.velocity_x + 
                self.back[2] * -self.velocity_z + 
                self.right[2] * -self.velocity_x) * self.speed * time.dt
        else:
            self.movementX += (self.forward[0] * held_keys["w"] / 5 + 
                self.left[0] * held_keys["a"] + 
                self.back[0] * held_keys["s"] + 
                self.right[0] * held_keys["d"]) / 1.4 * time.dt

            self.movementZ += (self.forward[2] * held_keys["w"] / 5 + 
                self.left[2] * held_keys["a"] + 
                self.back[2] * held_keys["s"] + 
                self.right[2] * held_keys["d"]) / 1.4 * time.dt

        # Collision Detection
        if self.movementX != 0:
            direction = (sign(self.movementX), 0, 0)
            x_ray = raycast(origin = self.world_position, direction = direction, traverse_target = self.level, ignore = [self, ])

            if x_ray.distance > self.scale_x / 2 + abs(self.movementX):
                self.x += self.movementX

        if self.movementZ != 0:
            direction = (0, 0, sign(self.movementZ))
            z_ray = raycast(origin = self.world_position, direction = direction, traverse_target = self.level, ignore = [self, ])

            if z_ray.distance > self.scale_z / 2 + abs(self.movementZ):
                self.z += self.movementZ

        # Looking around
        camera.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity * 30 * time.dt
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity * 30 * time.dt
        camera.rotation_x = min(max(-80, camera.rotation_x), 80)

        # Springs
        gun_movement = self.spring.update(time.dt)
        self.spring.shove(Vec3(mouse.x, mouse.y, 0))
        self.gun.x = gun_movement.x + 1
        self.gun.y = gun_movement.y - 0.75

    def input(self, key):
        if key == "space":
            if self.jump_count < 1:
                self.jump()
        if key == "right mouse down":
            rope_ray = raycast(camera.world_position, camera.forward, distance = 100, traverse_target = self.level, ignore = [self, camera, ])
            if rope_ray.hit:
                self.can_rope = True
                rope_point = rope_ray.world_point
                self.rope_entity = rope_ray.entity
                self.rope_pivot.position = rope_point
        elif key == "right mouse up":
            self.rope_pivot.position = self.position
            if self.can_rope:
                self.rope.disable()
                self.velocity_y += 10
            self.can_rope = False

class Gun(Entity):
    def __init__(self, player):
        super().__init__(
            model = "gun.obj",
            texture = "level.png",
            parent = camera,
            scale = 0.3,
            position = (1, -0.75, 1.7)
        )
        
        self.player = player
        self.level = self.player.level
        self.tip = Entity(parent = self, position = (-0.5, 1.3, 1.5))

        # Cooldown
        self.cooldown_t = 0
        self.cooldown_length = 0.3

        self.shooting = False
        self.can_shoot = True

    def update(self):
        self.cooldown_t += time.dt
        if self.cooldown_t >= self.cooldown_length:
            self.cooldown_t = 0
            self.can_shoot = True

            if held_keys["left mouse"]:
                self.shoot()
        
    def shoot(self):
        # Spawn bullet
        Bullet(self, self.tip.world_position)

        # Animate the gun
        self.animate_rotation((-30, 0, 0), duration = 0.1, curve = curve.linear)
        self.animate("z", 1.3, duration = 0.1, curve = curve.linear)
        self.animate("z", 1.7, 0.3, delay = 0.1, curve = curve.linear)
        self.animate_rotation((-15, 0, 0), 0.2, delay = 0.1, curve = curve.linear)
        self.animate_rotation((0, 0, 0), 0.4, delay = 0.12, curve = curve.linear)

        self.can_shoot = False
        self.shooting = True
        invoke(setattr, self, "shooting", False, delay = 0.3)

    def input(self, key):
        if key == "left mouse down" and self.can_shoot:
            self.shoot()

class Bullet(Entity):
    def __init__(self, gun, pos, speed = 2000, trail_colour = color.hex("#00baff")):
        super().__init__(
            model = "bullet.obj",
            texture = "level.png",
            scale = 0.08,
            position = pos
        )

        self.gun = gun
        self.speed = speed
        self.hit_player = False
        
        self.trail_thickness = 8
        self.trail = TrailRenderer(self.trail_thickness, trail_colour, color.clear, 5, parent = self)

        if hasattr(self.gun, "tip"):
            self.prev_pos = self.gun.player.crosshair.world_position
            self.rotation = camera.world_rotation
            self.is_player = True
            self.direction = self.forward + self.left / 80
        else:
            self.world_rotation = self.gun.world_rotation
            self.is_player = False
            self.direction = self.forward

    def update(self):
        self.position += self.direction * self.speed * time.dt
        
        if self.is_player:
            self.look_at(self.prev_pos)
            bullet_ray = raycast(self.world_position, self.forward, distance = 2, ignore = [self, self.gun])
            
            if bullet_ray.hit:
                for i in range(5):
                    p = Particles(bullet_ray.world_point - (self.forward * 5), Vec3(random.random(), random.random(), random.random()), 30)
                for e in self.gun.player.enemies:
                    if bullet_ray.entity == e:
                        e.health -= 1
                        if e.health <= 0:
                            for i in range(10):
                                p = Particles(e.world_position, Vec3(random.random(), random.randrange(-10, 10, 1) / 10, random.random()), spray_amount = 10, model = "particles", texture = "destroyed")
                            e.reset_pos()
                            e.health = 2
                destroy(self)

            destroy(self, delay = 3)
        else:
            bullet_ray = boxcast(self.world_position, self.forward, distance = 3, traverse_target = self.gun.player, ignore = [self, self.gun], thickness = (2, 2))
            if bullet_ray.hit:
                if not self.hit_player:
                    self.gun.player.health -= 1
                    self.gun.player.healthbar.value = self.gun.player.health
                    self.hit_player = True
                if self.gun.player.health <= 0:
                    self.gun.player.ded_text.enable()
                destroy(self)
            destroy(self, delay = 2)

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