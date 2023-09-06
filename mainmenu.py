from ursina import *
from ursina import curve

colourH = color.rgba(18, 152, 255, 180)
colourN = color.rgba(0, 0, 0, 0.7)
highlighted = lambda button: button.color == colourH

class MainMenu(Entity):
    def __init__(self, player, floating_islands, deserted_sands, mountainous_valley):
        super().__init__(
            parent = camera.ui
        )

        # Player
        self.player = player

        # Maps
        self.floating_islands = floating_islands
        self.deserted_sands = deserted_sands
        self.mountainous_valley = mountainous_valley

        # Menus
        self.mainmenu = Entity(parent = self, enabled = False)
        self.end_screen = Entity(parent = self, enabled = False)
        self.pause_menu = Entity(parent = self, enabled = False)
        self.maps_menu = Entity(parent = self, enabled = False)

        self.menus = [self.mainmenu, self.pause_menu, self.maps_menu]
        self.index = 0

        self.enable_end_screen = True

        # Animate the Menus
        for menu in self.menus:
            def animate_in_menu(menu = menu):
                for i, e in enumerate(menu.children):
                    e.original_scale = e.scale
                    e.scale -= 0.01
                    e.animate_scale(e.original_scale, delay = i * 0.05, duration = 0.1, curve = curve.out_quad)

                    e.alpha = 0
                    e.animate("alpha", 0.7, delay = i * 0.05, duration = 0.1, curve = curve.out_quad)

                    if hasattr(e, "text_entity"):
                        e.text_entity.alpha = 0
                        e.text_entity.animate("alpha", 1, delay = i * 0.05, duration = 0.1)

            if menu != self.pause_menu:
                menu.on_enable = animate_in_menu

        self.mainmenu.enable()

        # Main Menu
        self.start_button = Button(text = "Start", color = colourH, highlight_color = colourH, scale_y = 0.1, scale_x = 0.3, y = 0.05, parent = self.mainmenu)
        self.maps_button = Button(text = "Maps", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = -0.07, parent = self.mainmenu)
        self.quit_button = Button(text = "Quit", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = -0.19, parent = self.mainmenu)

        invoke(setattr, self.start_button, "color", colourH, delay = 0.5)

        # Endscreen
        retry_text = Text("Retry", scale = 4, origin = (0, 0.5), x = 0, y = 0.1, z = -100, parent = self.end_screen)
        press_enter = Text("Press Enter", scale = 2, origin = (0, 0.5), x = 0, y = 0, z = -100, parent = self.end_screen)
        self.highscore_text = Text(text = str(self.player.highscore), origin = (0, 0), size = 0.05, scale = (0.8, 0.8), position = window.top - (0, 0.1), parent = self.end_screen, z = -100)
        camera.overlay.parent = self.end_screen
        camera.overlay.color = color.rgba(220, 0, 0, 100)

        # Pause Menu
        self.resume_button = Button(text = "Resume", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = 0.05, parent = self.pause_menu)
        self.retry_button = Button(text = "Retry", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = -0.07, parent = self.pause_menu)
        self.mainmenu_button = Button(text = "Main Menu", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = -0.19, parent = self.pause_menu)
        self.pause_overlay = Entity(parent = self.pause_menu, model = "quad", scale = 99, color = color.rgba(20, 20, 20, 100), eternal = True, z = 10)

        # Maps Menu
        self.floating_islands_button = Button(text = "Floating Islands", color = colourN, highlighted_color = colourH, scale_y = 0.1, scale_x = 0.3, y = 0.05, parent = self.maps_menu)
        self.deserted_sands_button = Button(text = "Deserted Sands", color = colourN, highlighted_color = colourH, scale_y = 0.1, scale_x = 0.3, y = -0.07, parent = self.maps_menu)
        self.mountainous_valley_button = Button(text = "Mountainous Valley", color = colourN, highlighted_color = colourH, scale_y = 0.1, scale_x = 0.3, y = -0.19, parent = self.maps_menu)

    def update(self):
        if self.player.health <= 0:
            if self.enable_end_screen:
                self.end_screen.enable()
                self.enable_end_screen = False
                self.player.check_highscore()
                application.time_scale = 0.2
                self.player.dead = True
                self.highscore_text.text = "Highscore: " + str(self.player.highscore)

        if held_keys["enter"] and not self.enable_end_screen:
            self.player.reset()
            self.end_screen.disable()
            self.enable_end_screen = True
            
    def input(self, key):
        if key == "up arrow":
            for menu in self.menus:
                if menu.enabled:
                    self.index -= 1
                    if self.index <= -1:
                        self.index = 0
                    if isinstance(menu.children[self.index], Button):
                        menu.children[self.index].color = colourH
                        menu.children[self.index].highlight_color = colourH
                        for button in menu.children:
                            if menu.children[self.index] != button:
                                button.color = colourN
                                button.highlight_color = colourN
                    else:
                        self.index += 1

        elif key == "down arrow":
            for menu in self.menus:
                if menu.enabled:
                    self.index += 1
                    if self.index > len(menu.children) - 1:
                        self.index = len(menu.children) - 1
                    if isinstance(menu.children[self.index], Button):
                        menu.children[self.index].color = colourH
                        menu.children[self.index].highlight_color = colourH
                        for button in menu.children:
                            if menu.children[self.index] != button:
                                button.color = colourN
                                button.highlight_color = colourN
                    else:
                        self.index -= 1

        if key == "enter":
            # Main Menu
            if self.mainmenu.enabled:
                if highlighted(self.start_button):
                    self.start()
                elif highlighted(self.maps_button):
                    self.maps_menu.enable()
                    self.mainmenu.disable()
                    self.update_menu(self.maps_menu)
                elif highlighted(self.quit_button):
                    application.quit()

            # Pause Menu
            elif self.pause_menu.enabled:
                if highlighted(self.resume_button):
                    self.pause(False, False)
                elif highlighted(self.retry_button):
                    self.player.reset()
                    self.pause_menu.disable()
                elif highlighted(self.mainmenu_button):
                    self.player.disable()
                    self.player.reset()
                    for enemy in self.player.enemies:
                        enemy.disable()
                    self.mainmenu.enable()
                    self.pause_menu.disable()
                    self.update_menu(self.pause_menu)

            # Maps menu
            elif self.maps_menu.enabled:
                if highlighted(self.floating_islands_button):
                    for map in self.player.maps:
                        map.disable()
                    self.floating_islands.enable()
                    self.player.map = self.floating_islands
                    self.start()
                if highlighted(self.deserted_sands_button):
                    for map in self.player.maps:
                        map.disable()
                    self.deserted_sands.enable()
                    self.player.map = self.deserted_sands
                    self.start()
                if highlighted(self.mountainous_valley_button):
                    for map in self.player.maps:
                        map.disable()
                    self.mountainous_valley.enable()
                    self.player.map = self.mountainous_valley
                    self.player.position = (-5, 200, -10)
                    self.start() 

            # End Screen
            if self.player.health <= 0:
                self.end_screen.disable()
                self.enable_end_screen = True
                self.player.reset()

        if key == "escape":
            if self.maps_menu.enabled:
                self.maps_menu.disable()
                self.mainmenu.enable()

            # Pause Menu
            if self.player.enabled:
                self.pause()
                self.update_menu(self.pause_menu)

    def start(self):
        self.mainmenu.disable()
        self.maps_menu.disable()
        for enemy in self.player.enemies:
            enemy.enable()
        self.player.enable()

    def pause(self, opposite = True, pause = True):
        if opposite:
            self.pause_menu.enabled = not self.pause_menu.enabled
            if self.pause_menu.enabled:
                application.time_scale = 0.1
            else:
                application.time_scale = 1
        else:
            if pause:
                self.pause_menu.enable()
                application.time_scale = 0.1
            else:
                self.pause_menu.disable()
                application.time_scale = 1

    def update_menu(self, menu):
        for c in menu.children:
            c.color = colourN
            c.highlighted_color = colourN
        menu.children[0].color = colourH
        menu.children[0].highlighted_color = colourH
        self.index = 0