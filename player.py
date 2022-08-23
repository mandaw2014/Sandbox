from ursina import *

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)

class Player(Entity):
    def __init__(self, position, level, speed = 5, jump_height = 12):
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
        camera.fov = 70

        # Crosshair
        self.crosshair = Entity(model = "quad", color = color.black, parent = camera, rotation_z = 45, position = (0, 0, 1), scale = 0.008)

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

        self.mouse_sensitivity = 80

        self.level = level

        # Rope
        self.rope_pivot = Entity()
        self.rope = Entity(model = Mesh(vertices = [self.world_position, self.rope_pivot.world_position], mode = "line", thickness = 10), texture = "rope.png", color = color.orange, enabled = False)
        self.can_rope = False

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
                self.velocity_y -= 30 * time.dt
                self.grounded = False

        self.y += movementY * 50 * time.dt

        # Rope
        if self.can_rope:
            if held_keys["left mouse"]:
                if distance(self.position, self.rope_pivot.position) > 10:
                    self.position += ((self.rope_pivot.position - self.position).normalized() * 20 * time.dt)
                    self.rope.model.vertices.pop(0)
                    self.rope.model.vertices = [self.world_position + (0, 1, 0) + self.forward, self.rope_pivot.world_position]
                    self.rope.model.generate()
                    self.rope.enable()
                    if self.y < self.rope_pivot.y + 10:
                        self.velocity_y += 60 * time.dt
                    else:
                        self.velocity_y -= 50 * time.dt
                    self.velocity_x += 5 * time.dt
                    self.velocity_z += 5 * time.dt
                else:
                    self.rope.disable()

        # Velocity / Momentum
        if held_keys["w"]:
            self.velocity_z += 10 * time.dt if y_ray.hit else 2 * time.dt
        else:
            self.velocity_z = lerp(self.velocity_z, 0 if y_ray.hit else 1, time.dt * 2)
        if held_keys["a"]:
            self.velocity_x += 10 * time.dt if y_ray.hit else 2 * time.dt
        else:
            self.velocity_x = lerp(self.velocity_x, 0 if y_ray.hit else 1, time.dt * 2)
        if held_keys["s"]:
            self.velocity_z -= 10 * time.dt if y_ray.hit else 2 * time.dt
        else:
            self.velocity_z = lerp(self.velocity_z, 0 if y_ray.hit else 1, time.dt * 2)
        if held_keys["d"]:
            self.velocity_x -= 10 * time.dt if y_ray.hit else 2 * time.dt
        else:
            self.velocity_x = lerp(self.velocity_x, 0 if y_ray.hit else 1, time.dt * 2)

        # Movement
        movementX = (self.forward[0] * self.velocity_z + 
            self.left[0] * self.velocity_x + 
            self.back[0] * -self.velocity_z + 
            self.right[0] * -self.velocity_x) * self.speed * time.dt

        movementZ = (self.forward[2] * self.velocity_z + 
            self.left[2] * self.velocity_x + 
            self.back[2] * -self.velocity_z + 
            self.right[2] * -self.velocity_x) * self.speed * time.dt

        # Collision Detection
        if movementX != 0:
            direction = (sign(movementX), 0, 0)
            x_ray = raycast(origin = self.world_position, direction = direction, traverse_target = self.level, ignore = [self, ])

            if x_ray.distance > self.scale_x / 2 + abs(movementX):
                self.x += movementX

        if movementZ != 0:
            direction = (0, 0, sign(movementZ))
            z_ray = raycast(origin = self.world_position, direction = direction, traverse_target = self.level, ignore = [self, ])

            if z_ray.distance > self.scale_z / 2 + abs(movementZ):
                self.z += movementZ

        # Looking around
        camera.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity * 30 * time.dt
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity * 30 * time.dt
        camera.rotation_x = min(max(-80, camera.rotation_x), 80)

    def input(self, key):
        if key == "space":
            if self.jump_count < 1:
                self.jump()
        if key == "left mouse down":
            rope_ray = raycast(camera.world_position, camera.forward, distance = 250, ignore = [self, camera, self.level, ])
            if rope_ray.hit:
                self.can_rope = True
                rope_point = rope_ray.world_point
                self.rope_pivot.position = rope_point
        elif key == "left mouse up":
            self.rope_pivot.position = self.position
            if self.can_rope:
                self.rope.disable()
                # self.velocity_y = 40
            self.can_rope = False