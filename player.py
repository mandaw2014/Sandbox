from ursina import *
from ursina import curve

from ursina.prefabs.health_bar import HealthBar

from guns import *
from abilities import *

import json

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)
y_dir = lambda y: -1 if y < 0 else(1 if y > 0 else -1)

class Player(Entity):
    def __init__(self, position, speed = 5, jump_height = 14):
        super().__init__(
            model = "cube", 
            position = position,
            scale = (1.3, 1, 1.3), 
            visible_self = False,
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

        # Map
        self.map = None
        self.maps = []
        
        # Camera Shake
        self.can_shake = False
        self.shake_duration = 0.1
        self.shake_timer = 0
        self.shake_divider = 70 # the less, the more camera shake

        # Guns
        self.rifle = Rifle(self, True, enabled = True)
        self.shotgun = Shotgun(self, True, enabled = False)
        self.pistol = Pistol(self, True, enabled = False)
        self.minigun = MiniGun(self, True, enabled = False)
        self.rocket_launcher = RocketLauncher(self, True, enabled = False)

        self.guns = [self.rifle, self.shotgun, self.pistol, self.minigun, self.rocket_launcher]
        self.current_gun = 0

        # Abilities
        self.rope = Rope(self)
        self.dash_ability = DashAbility(self)
        self.slow_motion = SlowMotion(self, False)

        self.primary_abilities = [self.rope]
        self.secondary_abilities = [self.dash_ability, self.slow_motion]

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

        # Audio
        self.fall_sound = Audio("fall.wav", False)

    def jump(self):
        self.jumping = True
        self.velocity_y = self.jump_height
        self.jump_count += 1

    def update(self):
        movementY = self.velocity_y / 75
        self.velocity_y = clamp(self.velocity_y, -70, 100)

        direction = (0, sign(movementY), 0)

        # Main raycast for collision
        y_ray = raycast(origin = self.world_position, direction = (0, y_dir(self.velocity_y), 0), traverse_target = self.map, ignore = [self, ])
            
        if y_ray.distance <= self.scale_y * 1.5 + abs(movementY):
            if not self.grounded:
                self.velocity_y = 0
                self.grounded = True
                self.fall_sound.play()

            # Check if hitting a wall or steep slope
            if y_dir(self.velocity_y) == -1:
                if y_ray.world_normal.y > 0.7 and y_ray.world_point.y - self.world_y < 0.5:
                    # Set the y value to the ground's y value
                    if not held_keys["space"]:
                        self.y = y_ray.world_point.y + 1.4
                    self.jump_count = 0
                    self.jumping = False
        else:
            if not self.rope.can_rope:
                self.velocity_y -= 40 * time.dt
                self.grounded = False
                self.jump_count = 1

            self.y += movementY * 50 * time.dt

        # Sliding
        if self.sliding:
            camera.y = 0
            if y_ray.distance <= 2:
                slide_ray = raycast(self.world_position + self.forward, self.forward, distance = 8, traverse_target = self.map, ignore = [self, ])
                if not slide_ray.hit:
                    if hasattr(y_ray.world_point, "y"):
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

        # Velocity / Momentum
        if not self.sliding:
            movement = 10 if y_ray.distance < 5 and not self.rope.can_rope else 5

            if held_keys["w"]:
                self.velocity_z += movement * time.dt
            else:
                self.velocity_z = lerp(self.velocity_z, 0 if y_ray.distance < 5 else 1, time.dt * 3)
            if held_keys["a"]:
                self.velocity_x += movement * time.dt
            else:
                self.velocity_x = lerp(self.velocity_x, 0 if y_ray.distance < 5 else 1, time.dt * 3)
            if held_keys["s"]:
                self.velocity_z -= movement * time.dt
            else:
                self.velocity_z = lerp(self.velocity_z, 0 if y_ray.distance < 5 else 1, time.dt * 3)
            if held_keys["d"]:
                self.velocity_x -= movement * time.dt
            else:
                self.velocity_x = lerp(self.velocity_x, 0 if y_ray.distance < 5 else -1, time.dt * 3)

        # Movement
        if y_ray.distance <= 5 or self.rope.can_rope:
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
            air_movementX = 0.5 if self.movementX < 0.5 and self.movementX > -0.5 else 0.2
            air_movementZ = 0.5 if self.movementZ < 0.5 and self.movementZ > -0.5 else 0.2

            self.movementX += (self.forward[0] * held_keys["w"] * air_movementX + 
                self.left[0] * held_keys["a"] * air_movementX + 
                self.back[0] * held_keys["s"] * air_movementX + 
                self.right[0] * held_keys["d"] * air_movementX) / 2 * time.dt

            self.movementZ += (self.forward[2] * held_keys["w"] * air_movementZ + 
                self.left[2] * held_keys["a"] * air_movementZ + 
                self.back[2] * held_keys["s"] * air_movementZ + 
                self.right[2] * held_keys["d"] * air_movementZ) / 2 * time.dt

        # Collision Detection
        if self.movementX != 0:
            direction = (sign(self.movementX), 0, 0)
            x_ray = raycast(origin = self.world_position, direction = direction, traverse_target = self.map, ignore = [self, ])

            if x_ray.distance > self.scale_x / 2 + abs(self.movementX):
                self.x += self.movementX

        if self.movementZ != 0:
            direction = (0, 0, sign(self.movementZ))
            z_ray = raycast(origin = self.world_position, direction = direction, traverse_target = self.map, ignore = [self, ])

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
        if self.ability_bar.value <= 0:
            self.rope.rope_pivot.position = self.rope.position
            self.rope.rope.disable()
            self.rope.can_rope = False

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
        
        if key == "left shift":
            self.sliding = False # turned sliding off for now
            self.set_slide_rotation = True
        elif key == "left shift up":
            self.sliding = False

        if key == "1":
            if not self.rifle.enabled:
                for gun in self.guns:
                    gun.disable()
                self.rifle.enable()
        elif key == "2":
            if not self.shotgun.enabled:
                for gun in self.guns:
                    gun.disable()
                self.shotgun.enable()
        elif key == "3":
            if not self.pistol.enabled:
                for gun in self.guns:
                    gun.disable()
                self.pistol.enable()
        elif key == "4":
            if not self.minigun.enabled:
                for gun in self.guns:
                    gun.disable()
                self.minigun.enable()
        elif key == "5":
            if not self.rocket_launcher.enabled:
                for gun in self.guns:
                    gun.disable()
                self.rocket_launcher.enable()

        if key == "scroll up":
            self.current_gun = (self.current_gun - 1) % len(self.guns)
            for i, gun in enumerate(self.guns):
                if i == self.current_gun:
                    gun.enable()
                else:
                    gun.disable()
        
        if key == "scroll down":
            self.current_gun = (self.current_gun + 1) % len(self.guns)
            for i, gun in enumerate(self.guns):
                if i == self.current_gun:
                    gun.enable()
                else:
                    gun.disable()

    def shot_enemy(self):
        if not self.dead:
            self.score += 1
            self.score_text.text = str(self.score)
            if self.score > self.highscore:
                self.animate_text(self.score_text, 1.8, 1)

    def reset(self):
        if self.map == self.maps[0] or self.map == self.maps[1]:
            self.position = (-60, 15, -16)
        elif self.map == self.maps[2]:
            self.position = (-5, 200, -10)
        self.rotation = (0, -270, 0)
        self.velocity_x = 0
        self.velocity_y = 0
        self.velocity_z = 0
        self.health = 10
        self.healthbar.value = self.health
        self.ability_bar.value = 10
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

    def animate_text(self, text, top = 1.2, bottom = 0.6):
        """
        Animates the scale of text
        """
        text.animate_scale((top, top, top), curve = curve.out_expo)
        invoke(text.animate_scale, (bottom, bottom, bottom), delay = 0.4)