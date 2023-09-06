from ursina import *
from direct.stdpy import thread

from player import Player
from enemy import Enemy, BigEnemy

from mainmenu import MainMenu

from maps import FloatingIslands, DesertedSands, MountainousValley

from scene_lighting import SceneLighting

Text.default_font = "./assets/Roboto.ttf"
Text.default_resolution = Text.size * 1080

app = Ursina()
window.fullscreen = True
window.borderless = False
window.cog_button.disable()
window.collider_counter.disable()
window.entity_counter.disable()
window.fps_counter.disable()
window.exit_button.disable()

scene.fog_density = 0.001

# Starting new thread for assets
def load_assets():
    models_to_load = [
        "floatingislands", "desertedsands", "mountainous_valley", "jumppad", "particle", "particles", "enemy", "bigenemy" "pistol", 
        "shotgun", "rifle", "pistol", "minigun", "minigun-barrel", "rocket-launcher", "rocket", "bullet",
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

floating_islands = FloatingIslands(player, enabled = True)
deserted_sands = DesertedSands(player, enabled = False)
mountainous_valley = MountainousValley(player, enabled = False)

player.map = floating_islands
player.maps = [floating_islands, deserted_sands, mountainous_valley]

# Enemy
for enemy in range(10):
    i = random.randint(0, 2)
    if i == 0:
        e = BigEnemy(player, position = Vec3(random.randint(-50, 50)))
    else:
        e = Enemy(player, position = Vec3(random.randint(-50, 50)))

    e.disable()
    player.enemies.append(e)

mainmenu = MainMenu(player, floating_islands, deserted_sands, mountainous_valley)

# Lighting + Shadows
scene_lighting = SceneLighting(ursina = app, player = player, sun_direction = (-0.7, -0.9, 0.5), shadow_resolution = 4096, sky_texture = "sky")

def input(key):
    if key == "g":
        player.reset()

# def update():
#     print(player.position)

app.run()