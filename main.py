from ursina import *
from direct.stdpy import thread

from player import Player
from enemy import Enemy, BigEnemy

from mainmenu import MainMenu

from levels import SkyLevel, DesertLevel

from sun import SunLight

Text.default_font = "./assets/Roboto.ttf"
Text.default_resolution = Text.size * 1080

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
        "skylevel", "desertlevel", "jumppad" "particle", "particles", "enemy", "bigenemy" "pistol", 
        "shotgun", "rifle", "pistol", "minigun", "minigun-barrel", "bullet",
    ]

    textures_to_load = [
        "level", "particle", "destroyed", "jetpack", "sky", "rope", "hit"
    ]

    for i, m in enumerate(models_to_load):
        load_model(m)

    for i, t in enumerate(textures_to_load):
        load_texture(t)

try:
    thread.start_new_thread(function = load_assets, args = "")
except Exception as e:
    print("error starting thread", e)

player = Player((-60, 50, -16)) # Flat: (-47, 50, -94) # Rope: (-61, 100, 0)
player.disable()

sky_level = SkyLevel(player, enabled = True)
desert_level = DesertLevel(player, enabled = False)

player.level = sky_level

# Enemy
for enemy in range(5):
    i = random.randint(0, 2)
    if i == 0:
        e = BigEnemy(player, position = Vec3(random.randint(-50, 50)))
    else:
        e = Enemy(player, position = Vec3(random.randint(-50, 50)))

    e.disable()
    player.enemies.append(e)

mainmenu = MainMenu(player)

# Lighting + shadows
sun = SunLight(direction = (-0.7, -0.9, 0.5), resolution = 3072, player = player)
ambient = AmbientLight(color = Vec4(0.5, 0.55, 0.66, 0) * 1.3)

render.setShaderAuto()

Sky(texture = "sky", scale = 8000)

def input(key):
    if key == "g":
        player.reset()

def update():
    print(player.minigun.position)

app.run()