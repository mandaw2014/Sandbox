from ursina import *
from ursina import curve

class Ability(Entity):
    def __init__(self, player, ability_enabled = True):
        super().__init__(
            parent = player
        )

        self.player = player
        self.ability_enabled = ability_enabled
        self.shift_count = 0

class Rope(Ability):
    def __init__(self, player, enabled = True):
        super().__init__(
            player, enabled
        )

        self.rope_pivot = Entity()
        self.rope = Entity(model = Mesh(vertices = [self.world_position, self.rope_pivot.world_position], mode = "line", thickness = 15, colors = [color.hex("#ff8b00")]), texture = "rope.png", enabled = False)
        self.rope_position = self.position
        self.can_rope = False
        self.rope_length = 200
        self.max_rope_length = False
        self.below_rope = False

        # Audio
        self.rope_sound = Audio("rope.wav", False)

    def update(self):
        if self.ability_enabled:
            if self.can_rope and self.player.ability_bar.value > 0:
                if held_keys["right mouse"]:
                    if distance(self.player.position, self.rope_pivot.position) > 10:
                        if distance(self.player.position, self.rope_pivot.position) < self.rope_length and not self.player.grounded:
                            self.player.position += ((self.rope_pivot.position - self.player.position).normalized() * 20) * time.dt
                            self.player.velocity_z += 2 * time.dt  
                        self.rope_position = lerp(self.rope_position, self.rope_pivot.world_position, time.dt * 20)
                        self.rope.model.vertices.pop(0)
                        self.rope.model.vertices = [self.player.position - (0, 5, 0) + (self.player.forward * 4) + (self.player.left * 2), self.rope_position]
                        self.rope.model.generate()
                        self.rope.enable()
                        if self.player.y < self.rope_pivot.y:
                            self.player.velocity_y += 40 * time.dt
                        else:
                            self.player.velocity_y -= 60 * time.dt

                        if (self.rope_pivot.y - self.player.y) > self.rope_length:
                            self.below_rope = True
                            invoke(setattr, self, "below_rope", False, delay = 5)

                        if self.below_rope:
                            self.player.velocity_y += 50 * time.dt
                    else:
                        self.rope.disable()
                    if distance(self.player.position, self.rope_pivot.position) > self.rope_length:
                        self.max_rope_length = True
                        invoke(setattr, self, "max_rope_length", False, delay = 2)
                    if self.max_rope_length:
                        self.player.position += ((self.rope_pivot.position - self.player.position).normalized() * 25 * time.dt)
                        self.player.velocity_z -= 5 * time.dt
                        self.player.velocity_y -= 80 * time.dt

                    self.player.using_ability = True
                    self.player.ability_bar.value -= 3 * time.dt

    def input(self, key):
        if self.ability_enabled:
            if key == "right mouse down" and self.player.ability_bar.value > 0:
                rope_ray = raycast(camera.world_position, camera.forward, distance = 100, traverse_target = self.player.map, ignore = [self, camera, ])
                if rope_ray.hit:
                    self.can_rope = True
                    rope_point = rope_ray.world_point
                    self.rope_entity = rope_ray.entity
                    self.rope_pivot.position = rope_point
                    self.rope_position = self.position
                    self.rope_sound.pitch = random.uniform(0.7, 1)
                    self.rope_sound.play()
            elif key == "right mouse up":
                self.rope_pivot.position = self.position
                if self.can_rope and self.player.ability_bar.value > 0:
                    self.rope.disable()
                    self.player.velocity_y += 10
                self.can_rope = False
                invoke(setattr, self.player, "using_ability", False, delay = 2)

class DashAbility(Ability):
    def __init__(self, player, enabled = True):
        super().__init__(
            player, enabled
        )

        self.dashing = False

        # Audio
        self.dash_sound = Audio("dash.wav", False)
        self.dash_sound.volume = 0.8

    def update(self):
        if self.ability_enabled:
            if self.dashing and not held_keys["right mouse"]:
                if held_keys["a"]:
                    self.player.animate_position(self.player.position + (camera.left * 40), duration = 0.2, curve = curve.in_out_quad)
                elif held_keys["d"]:
                    self.player.animate_position(self.player.position + (camera.right * 40), duration = 0.2, curve = curve.in_out_quad)
                else:
                    self.player.animate_position(self.player.position + (camera.forward * 40), duration = 0.2, curve = curve.in_out_quad)
                
                camera.animate("fov", 120, duration = 0.2, curve = curve.in_quad)
                camera.animate("fov", 100, curve = curve.out_quad, delay = 0.2)

                self.dashing = False
                self.player.velocity_y = 0

                self.player.shake_camera(0.3, 100)

                self.dash_sound.play()

                self.player.movementX = (self.player.forward[0] * self.player.velocity_z + 
                    self.player.left[0] * self.player.velocity_x + 
                    self.player.back[0] * -self.player.velocity_z + 
                    self.player.right[0] * -self.player.velocity_x) * self.player.speed * time.dt

                self.player.movementZ = (self.player.forward[2] * self.player.velocity_z + 
                    self.player.left[2] * self.player.velocity_x + 
                    self.player.back[2] * -self.player.velocity_z + 
                    self.player.right[2] * -self.player.velocity_x) * self.player.speed * time.dt

    def input(self, key):
        if self.ability_enabled:
            if key == "left shift":
                self.shift_count += 1
                if self.shift_count >= 2 and self.player.ability_bar.value >= 5:
                    self.dashing = True
                    self.player.ability_bar.value -= 5
                    self.player.using_ability = True
                    invoke(setattr, self.player, "using_ability", False, delay = 2)
                invoke(setattr, self, "shift_count", 0, delay = 0.2)

class SlowMotion(Ability):
    def __init__(self, player, enabled = True):
        super().__init__(player, enabled)
        
        self.slow_motion = False
        self.start_slow_motion = False
        self.vignette = Entity(model = "quad", texture = "vignette.png", parent = camera.ui, scale_x = 2, enabled = False)
    
    def update(self):
        if self.ability_enabled:
            if self.start_slow_motion:
                application.time_scale = 0.5
                self.vignette.enable()
                self.player.using_ability = True
                self.start_slow_motion = False

            if self.slow_motion:
                self.player.ability_bar.value -= 3 * time.dt
                self.player.using_ability = True

            if self.player.ability_bar.value <= 1:
                application.time_scale = 1
                self.vignette.disable()
                self.player.using_ability = False
                self.shift_count = 0

    def input(self, key):
        if self.ability_enabled:
            if key == "left shift":
                self.shift_count += 1
                if self.shift_count >= 2 and self.player.ability_bar.value >= 5:
                    self.slow_motion = True
                    self.start_slow_motion = True
                invoke(setattr, self, "shift_count", 0, delay = 0.2)
            elif key == "left shift up":
                self.slow_motion = False
                application.time_scale = 1
                self.vignette.disable()
                self.player.using_ability = False