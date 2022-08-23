from ursina import *
from player import Player
from sun import SunLight

if sys.platform != "darwin":
    window.fullscreen = True
else:
    # window.size = window.fullscreen_size
    window.position = Vec2(
        int((window.screen_resolution[0] - window.fullscreen_size[0]) / 2),
        int((window.screen_resolution[1] - window.fullscreen_size[1]) / 2)
    )

app = Ursina(vsync = 10)
window.borderless = False
window.cog_button.disable()
# window.fps_counter.disable()
window.exit_button.disable()

class GrapplePoint(Entity):
    def __init__(self, position = (0, 0, 0)):
        super().__init__(
            model = "points.obj",
            scale = (3, 0.9, 3),
            texture = "points.png",
            position = position,
            collider = "box"
        )

level = Entity(model = "level.obj", texture = "level.png", scale = (50, 50, 50), collider = "mesh")
lava = Entity(model = "lava.obj", texture = "lava.png", scale = (50, 50, 50), collider = "mesh")

grapple_1 = GrapplePoint((0, 20, 75))
grapple_2 = GrapplePoint((0, 20, 150))
grapple_3 = GrapplePoint((0, 20, 225))
grapple_4 = GrapplePoint((0, 20, 300))
grapple_5 = GrapplePoint((0, 20, 375))

player = Player((0, 100, 0), level)

# Lighting + shadows
sun = SunLight(direction = (-0.7, -0.9, 0.5), resolution = 3072, player = player)
ambient = AmbientLight(color = Vec4(0.5, 0.55, 0.66, 0) * 1.5)

render.setShaderAuto()

Sky()

def update():
    print(player.velocity_y)
    if held_keys["escape"]:
        mouse.locked = False
    if held_keys["left mouse"]:
        mouse.locked = True

    if held_keys["g"]:
        player.position = (0, 20, 0)

    if held_keys["q"]:
        player.position = (0, 52, 0)

    if player.intersects(lava):
        player.position = (0, 20, 0)

app.run()