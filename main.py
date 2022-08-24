from ursina import *
from player import Player
from sun import SunLight

if sys.platform != "darwin":
    window.fullscreen = True
else:
    window.size = window.fullscreen_size
    window.position = Vec2(
        int((window.screen_resolution[0] - window.fullscreen_size[0]) / 2),
        int((window.screen_resolution[1] - window.fullscreen_size[1]) / 2)
    )

app = Ursina()
window.borderless = False
window.cog_button.disable()
# window.fps_counter.disable()
window.exit_button.disable()

level = Entity(model = "level.obj", texture = "level.png", scale = (30, 30, 30), collider = "mesh")

player = Player((20, 100, 0), level)

# Lighting + shadows
sun = SunLight(direction = (-0.7, -0.9, 0.5), resolution = 3072, player = player)
ambient = AmbientLight(color = Vec4(0.5, 0.55, 0.66, 0) * 1.5)

render.setShaderAuto()

Sky()

def update():
    if held_keys["escape"]:
        mouse.locked = not mouse.locked

    if held_keys["g"]:
        player.position = (5, 20, 0)

app.run()