from ursina import *
from direct.stdpy import thread

from player import Player
from enemy import Enemy

from mainmenu import MainMenu

from levels import SkyLevel, Sandbox1, Sandbox2, TestLevel

from sun import SunLight

Text.default_font = "./assets/Roboto.ttf"

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
        "sandbox1", "testlevel", "sandbox2", "skylevel", "particle", "particles", "enemy", "gun", "bullet"
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

player = Player((-60, 15, -16)) # Flat: (-47, 50, -94) # Rope: (-61, 100, 0)
player.disable()

skylevel = SkyLevel(player, enabled = True)
sandbox1 = Sandbox1(player, enabled = False)
sandbox2 = Sandbox2(player, enabled = False)
testlevel = TestLevel(player, enabled = False)

level = skylevel
player.level = level

# Enemy
for enemy in range(5):
    e = Enemy(player, position = Vec3(random.randint(-50, 50)))
    e.disable()
    player.enemies.append(e)

mainmenu = MainMenu(player)

# Lighting + shadows
sun = SunLight(direction = (-0.7, -0.9, 0.5), resolution = 3072, player = player)
ambient = AmbientLight(color = Vec4(0.5, 0.55, 0.66, 0) * 1.3)

render.setShaderAuto()

Sky(texture = "sky", scale = 8000)

def update():
    print(player.position)
    if held_keys["r"]:
        player.reset()

app.run()