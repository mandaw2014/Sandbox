from ursina import *
from ursina import curve

from ursina.prefabs.trail_renderer import TrailRenderer
from ursina.prefabs.health_bar import HealthBar

from particles import Particles

import json

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)

class Player(Entity):
    def __init__(self, position, speed = 5, jump_height = 14):
        super().__init__(
            model = "cube", 
            position = position,
            scale = (1.3, 1, 1.3), 
            visible_self = False,
            collider = "box",
            rotation_y = -270
        )

        # Camera
        mouse.locked = True
        camera.parent = self
        camera.position = (0, 2, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 100

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

        self.mouse_sensitivity = 50

        # Level
        self.level = None
        
        # Camera Shake
        self.can_shake = False
        self.shake_duration = 0.1
        self.shake_timer = 0
        self.shake_divider = 70 # the less, the more camera shake

        # Guns
        self.rifle = Rifle(self, enabled = True)
        self.shotgun = Shotgun(self, enabled = False)
        self.pistol = Pistol(self, enabled = False)

        # Rope
        self.rope_pivot = Entity()
        self.rope = Entity(model = Mesh(vertices = [self.world_position, self.rope_pivot.world_position], mode = "line", thickness = 15, colors = [color.hex("#ff8b00")]), texture = "rope.png", enabled = False)
        self.can_rope = False
        self.rope_length = 100
        self.max_rope_length = False
        self.below_rope = False

        # Sliding
        self.sliding = False
        self.slope = False
        self.slide_pivot = Entity()
        self.set_slide_rotation = False

        # Enemies
        self.enemies = []

        # Health
        self.healthbar = HealthBar(10, bar_color = color.hex("#ff1e1e"), roundness = 0, y = window.bottom_left[1] + 0.1, scale_y = 0.03, scale_x = 0.3)
        self.healthbar.text_entity.disable()
        self.ability_bar = HealthBar(10, bar_color = color.hex("#50acff"), roundness = 0, position = window.bottom_left + (0.12, 0.05), scale_y = 0.007, scale_x = 0.2)
        self.ability_bar.text_entity.disable()
        self.ability_bar.animation_duration = 0
        
        self.health = 10
        self.using_ability = False
        self.dead = False
    
        # Score
        self.score = 0
        self.score_text = Text(text = str(self.score), origin = (0, 0), size = 0.05, scale = (1, 1), position = window.top_right - (0.1, 0.1))
        self.score_text.text = str(self.score)

        # Get highscore from json file
        path = os.path.dirname(sys.argv[0])
        self.highscore_path = os.path.join(path, "./highscores/highscore.json")
        
        try:
            with open(self.highscore_path, "r") as hs:
                highscore_file = json.load(hs)
                self.highscore = highscore_file["highscore"]
        except FileNotFoundError:
            with open(self.highscore_path, "w+") as hs:
                json.dump({"highscore": 0}, hs, indent = 4)
                self.highscore = 0

        # Dash
        self.dashing = False
        self.can_dash = True
        self.shift_count = 0

    def jump(self):
        self.jumping = True
        self.velocity_y = self.jump_height
        self.jump_count += 1

    def update(self):
        movementY = self.velocity_y * time.dt
        self.velocity_y = clamp(self.velocity_y, -70, 100)

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

        # Sliding
        if self.sliding:
            camera.y = 0
            slide_ray = raycast(self.world_position + self.forward, self.forward, distance = 8, traverse_target = self.level, ignore = [self, ])
            if not slide_ray.hit:
                if hasattr(y_ray.world_point, "y"):
                    if y_ray.distance <= 2:
                        self.y = y_ray.world_point.y + 1.4

                        if y_ray.world_normal[2] * 10 < 0:
                            self.velocity_z -= y_ray.world_normal[2] * 10 * time.dt
                        if y_ray.world_normal[2] * 10 > 0:
                            self.velocity_z += y_ray.world_normal[2] * 10 * time.dt
            elif slide_ray.hit:
                self.velocity_z = -10
                if self.velocity_z <= -1:
                    self.velocity_z = -1
                if hasattr(y_ray.world_point, "y"):
                    self.y = y_ray.world_point.y + 1.4
            
            if self.set_slide_rotation:
                self.slide_pivot.rotation = camera.world_rotation
                self.set_slide_rotation = False
        else:
            camera.y = 2

        self.y += movementY * 50 * time.dt

        # Rope
        if self.can_rope and self.ability_bar.value > 0:
            if held_keys["right mouse"]:
                if distance(self.position, self.rope_pivot.position) > 10:
                    if distance(self.position, self.rope_pivot.position) < self.rope_length:
                        self.position += ((self.rope_pivot.position - self.position).normalized() * 20 * time.dt)
                        self.velocity_z += 2 * time.dt  
                    self.rope.model.vertices.pop(0)
                    self.rope.model.vertices = [self.position - (0, 5, 0) + (self.forward * 4) + (self.left * 2), self.rope_pivot.world_position]
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

                self.using_ability = True
                self.ability_bar.value -= 3 * time.dt

        # Dashing
        if self.dashing and not self.sliding and not held_keys["right mouse"]:
            if held_keys["a"]:
                self.animate_position(self.position + (camera.left * 40), duration = 0.2, curve = curve.in_out_quad)
            elif held_keys["d"]:
                self.animate_position(self.position + (camera.right * 40), duration = 0.2, curve = curve.in_out_quad)
            else:
                self.animate_position(self.position + (camera.forward * 40), duration = 0.2, curve = curve.in_out_quad)
            
            camera.animate("fov", 130, duration = 0.2, curve = curve.in_quad)
            camera.animate("fov", 100, curve = curve.out_quad, delay = 0.2)

            self.dashing = False
            self.velocity_y = 0

            self.shake_camera(0.3, 100)

            self.movementX = (self.forward[0] * self.velocity_z + 
                self.left[0] * self.velocity_x + 
                self.back[0] * -self.velocity_z + 
                self.right[0] * -self.velocity_x) * self.speed * time.dt

            self.movementZ = (self.forward[2] * self.velocity_z + 
                self.left[2] * self.velocity_x + 
                self.back[2] * -self.velocity_z + 
                self.right[2] * -self.velocity_x) * self.speed * time.dt

        # Velocity / Momentum
        if not self.sliding:
            if held_keys["w"]:
                self.velocity_z += 10 * time.dt if y_ray.distance < 5 and not self.can_rope else 5 * time.dt
            else:
                self.velocity_z = lerp(self.velocity_z, 0 if y_ray.distance < 5 else 1, time.dt * 3)
            if held_keys["a"]:
                self.velocity_x += 10 * time.dt if y_ray.distance < 5 and not self.can_rope else 5 * time.dt
            else:
                self.velocity_x = lerp(self.velocity_x, 0 if y_ray.distance < 5 else 1, time.dt * 3)
            if held_keys["s"]:
                self.velocity_z -= 10 * time.dt if y_ray.distance < 5 and not self.can_rope else 5 * time.dt
            else:
                self.velocity_z = lerp(self.velocity_z, 0 if y_ray.distance < 5 else 1, time.dt * 3)
            if held_keys["d"]:
                self.velocity_x -= 10 * time.dt if y_ray.distance < 5 and not self.can_rope else 5 * time.dt
            else:
                self.velocity_x = lerp(self.velocity_x, 0 if y_ray.distance < 5 else -1, time.dt * 3)

        # Movement
        if y_ray.distance <= 5 or self.can_rope:
            if not self.sliding:
                self.movementX = (self.forward[0] * self.velocity_z + 
                    self.left[0] * self.velocity_x + 
                    self.back[0] * -self.velocity_z + 
                    self.right[0] * -self.velocity_x) * self.speed * time.dt

                self.movementZ = (self.forward[2] * self.velocity_z + 
                    self.left[2] * self.velocity_x + 
                    self.back[2] * -self.velocity_z + 
                    self.right[2] * -self.velocity_x) * self.speed * time.dt
        else:
            self.movementX += ((self.forward[0] * held_keys["w"] / 5 + 
                self.left[0] * held_keys["a"] + 
                self.back[0] * held_keys["s"] + 
                self.right[0] * held_keys["d"]) / 1.4) * time.dt

            self.movementZ += ((self.forward[2] * held_keys["w"] / 5 + 
                self.left[2] * held_keys["a"] + 
                self.back[2] * held_keys["s"] + 
                self.right[2] * held_keys["d"]) / 1.4) * time.dt

        if self.sliding:
            self.movementX += (((self.slide_pivot.forward[0] * self.velocity_z) +
                self.left[0] * held_keys["a"] * 2 + 
                self.right[0] * held_keys["d"] * 2) / 10) * time.dt

            self.movementZ += (((self.slide_pivot.forward[2] * self.velocity_z) + 
                self.left[2] * held_keys["a"] * 2 + 
                self.right[2] * held_keys["d"] * 2)) / 10 * time.dt

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

        # Camera
        camera.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity
        camera.rotation_x = min(max(-90, camera.rotation_x), 90)

        # Camera Shake
        if self.can_shake:
            camera.position = self.prev_camera_pos + Vec3(random.randrange(-10, 10), random.randrange(-10, 10), random.randrange(-10, 10)) / self.shake_divider

        # Abilities
        n = clamp(self.ability_bar.value, 0, self.ability_bar.max_value)
        self.ability_bar.bar.scale_x = n / self.ability_bar.max_value

        if not self.using_ability and self.ability_bar.value < 10:
            self.ability_bar.value += 5 * time.dt
        if self.ability_bar.value <= 0 and self.can_rope:
            self.can_rope = False
            self.rope.disable()
            self.velocity_y += 10
            self.rope_pivot.position = self.position

        # Resets the player if falls of the map
        if self.y <= -100:
            self.position = (-60, 15, -16)
            self.rotation_y = -270
            self.velocity_x = 0
            self.velocity_y = 0
            self.velocity_z = 0
            self.health -= 5
            self.healthbar.value = self.health

    def input(self, key):
        if key == "space":
            if self.jump_count < 1:
                self.jump()
        if key == "right mouse down" and self.ability_bar.value > 3:
            rope_ray = raycast(camera.world_position, camera.forward, distance = 100, traverse_target = self.level, ignore = [self, camera, ])
            if rope_ray.hit:
                self.can_rope = True
                rope_point = rope_ray.world_point
                self.rope_entity = rope_ray.entity
                self.rope_pivot.position = rope_point
        elif key == "right mouse up":
            self.rope_pivot.position = self.position
            if self.can_rope and self.ability_bar.value > 0:
                self.rope.disable()
                self.velocity_y += 10
            self.can_rope = False
            invoke(setattr, self, "using_ability", False, delay = 2)
        
        if key == "left shift":
            self.sliding = True
            self.set_slide_rotation = True
            self.shift_count += 1
            if self.shift_count >= 2 and self.ability_bar.value >= 5:
                self.dashing = True
                self.ability_bar.value -= 5
                self.using_ability = True
            invoke(setattr, self, "shift_count", 0, delay = 0.2)
            invoke(setattr, self, "using_ability", False, delay = 2)
        elif key == "left shift up":
            self.sliding = False

        if key == "1":
            self.rifle.enable()
            self.shotgun.disable()
            self.pistol.disable()
        elif key == "2":
            self.pistol.disable()
            self.shotgun.enable()
            self.rifle.disable()
        elif key == "3":
            self.pistol.enable()
            self.shotgun.disable()
            self.rifle.disable()

    def shot_enemy(self):
        if not self.dead:
            self.score += 1
            self.score_text.text = str(self.score)

    def reset(self):
        self.position = (-60, 15, -16)
        self.rotation_y = -270
        self.velocity_x = 0
        self.velocity_y = 0
        self.velocity_z = 0
        self.health = 10
        self.healthbar.value = self.health
        self.dead = False
        self.score = 0
        self.score_text.text = self.score
        application.time_scale = 1
        for enemy in self.enemies:
            enemy.reset_pos()

    def shake_camera(self, duration = 0.1, divider = 70):
        self.can_shake = True
        self.shake_duration = duration
        self.shake_divider = divider
        self.prev_camera_pos = camera.position
        invoke(setattr, self, "can_shake", False, delay = self.shake_duration)
        invoke(setattr, camera, "position", self.prev_camera_pos, delay = self.shake_duration)

    def check_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            with open(self.highscore_path, "w") as hs:
                json.dump({"highscore": int(self.highscore)}, hs, indent = 4)    

class Gun(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            parent = camera,
            scale = 0.3,
            position = (0.5, -0.75, 1.7),
            **kwargs
        )
        
        self.player = player
        self.level = self.player.level
        self.tip = Entity(parent = self, position = (-0.5, 1.3, 1.5))

        self.pos_x = 0.5
        self.pos_y = -0.75

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

    def update(self):
        self.cooldown_t += time.dt
        if self.cooldown_t >= self.cooldown_length:
            self.cooldown_t = 0
            self.can_shoot = True

            if held_keys["left mouse"] and not self.started_shooting:
                self.shoot()

        # Springs
        if self.start_spring:
            gun_movement = self.spring.update(time.dt)
            self.spring.shove(Vec3(mouse.x, mouse.y, 0))
            self.x = gun_movement.x + self.pos_x
            self.y = gun_movement.y + self.pos_y
    
    def shoot(self):
        # Spawn bullet
        if self.gun_type == "pistol":
            Bullet(self, self.tip.world_position)
        elif self.gun_type == "shotgun":
            for i in range(random.randint(2, 3)):
                b = Bullet(self, self.tip.world_position)
                b.direction = b.forward + (self.left * random.randrange(-10, 10) / 700) + (self.up * random.randrange(-10, 10) / 700)
        elif self.gun_type == "rifle":
            Bullet(self, self.tip.world_position)

        # Animate the gun
        if self.gun_type == "pistol" or self.gun_type == "shotgun":
            self.animate_rotation((-30, 0, 0), duration = 0.1, curve = curve.linear)
            self.animate("z", 1, duration = 0.03, curve = curve.linear)
            self.animate("z", 1.5, 0.2, delay = 0.1, curve = curve.linear)
            self.animate_rotation((-15, 0, 0), 0.2, delay = 0.1, curve = curve.linear)
            self.animate_rotation((0, 0, 0), 0.4, delay = 0.12, curve = curve.linear)
        else:
            self.animate_rotation((-20, 0, 0), duration = 0.1, curve = curve.linear)
            self.animate("z", 1.2, duration = 0.03, curve = curve.linear)
            self.animate("z", 1.5, 0.2, delay = 0.1, curve = curve.linear)
            self.animate_rotation((-10, 0, 0), 0.2, delay = 0.1, curve = curve.linear)
            self.animate_rotation((0, 0, 0), 0.4, delay = 0.12, curve = curve.linear)

        self.can_shoot = False

        self.player.shake_camera(0.1, self.shake_divider)

    def input(self, key):
        if key == "left mouse down" and self.can_shoot:
            self.shoot()
            self.started_shooting = True
            invoke(setattr, self, "started_shooting", False, delay = self.cooldown_length / 2)

    def on_enable(self):
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

class Pistol(Gun):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "pistol.obj",
            texture = "level.png",
            player = player,
            **kwargs
        )

        self.gun_type = "pistol"

class Shotgun(Gun):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "shotgun.obj",
            texture = "level.png",
            player = player,
            **kwargs
        )

        self.gun_type = "shotgun"
        self.tip.z = 2

        self.pos_x = 0.6
        self.pos_y = -0.5

        self.damage = 2

        self.shake_divider = 40
        self.cooldown_length = 0.8

class Rifle(Gun):
    def __init__(self, player, **kwargs):
        super().__init__(
            model = "rifle.obj",
            texture = "level.png",
            player = player,
            **kwargs
        )

        self.gun_type = "rifle"
        self.tip.z = 3

        self.pos_x = 0.6
        self.pos_y = -0.5

        self.damage = 0.8

        self.shake_divider = 120
        self.cooldown_length = 0.2

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
            bullet_ray = raycast(self.world_position, self.forward, distance = 2, ignore = [self, self.gun])
            
            if bullet_ray.hit:
                for i in range(5):
                    p = Particles(bullet_ray.world_point - (self.forward * 5), Vec3(random.random(), random.random(), random.random()), 30)
                for e in self.gun.player.enemies:
                    if bullet_ray.entity == e:
                        e.health -= self.gun.damage
                        if e.health <= 0:
                            for i in range(5):
                                p = Particles(e.world_position, Vec3(random.random(), random.randrange(-10, 10, 1) / 10, random.random()), spray_amount = 10, model = "particles", texture = "destroyed")
                            e.reset_pos()
                            e.health = 2
                            self.gun.player.shot_enemy()
                destroy(self)

            destroy(self, delay = 2)
        else:
            level_ray = raycast(self.world_position, self.forward, distance = 3, traverse_target = self.gun.player.level, ignore = [self, self.gun])
            if distance(self, self.gun.player) <= 3:
                if not self.hit_player:
                    self.gun.player.health -= 1
                    self.gun.player.healthbar.value = self.gun.player.health
                    self.hit_player = True
                destroy(self)
            if level_ray.hit:
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