from ursina import *
from direct.stdpy import thread
from player import Player
from sun import SunLight
from enemy import Enemy

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
window.fps_counter.disable()
window.exit_button.disable()

# Starting new thread for assets
def load_assets():
    models_to_load = [
        "level", "particle", "particles", "enemy", "gun", "bullet"
    ]

    textures_to_load = [
        "level", "particle", "destroyed", "jetpack", "sky", "rope"
    ]

    for i, m in enumerate(models_to_load):
        load_model(m)

    for i, t in enumerate(textures_to_load):
        load_texture(t)

try:
    thread.start_new_thread(function = load_assets, args = "")
except Exception as e:
    print("error starting thread", e)

level = Entity(model = "level.obj", texture = "level.png", scale = (30, 30, 30), collider = "mesh")

player = Player((-61, 100, 0), level)

# Enemy
for enemy in range(5):
    e = Enemy(player, position = Vec3(random.randint(-50, 50)))
    player.enemies.append(e)

# Lighting + shadows
sun = SunLight(direction = (-0.7, -0.9, 0.5), resolution = 3072, player = player)
ambient = AmbientLight(color = Vec4(0.5, 0.55, 0.66, 0) * 1.5)

render.setShaderAuto()

Sky(texture = "sky")

def update():
    if held_keys["g"]:
        player.position = (-61, 25, 0)

app.run()