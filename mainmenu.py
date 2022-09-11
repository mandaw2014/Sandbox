from ursina import *

colourH = color.rgba(18, 152, 255, 180)
highlighted = lambda button: button.color == colourH

class MainMenu(Entity):
    def __init__(self, player):
        super().__init__(
            parent = camera.ui
        )

        # Player
        self.player = player

        # Menus
        self.mainmenu = Entity(parent = self, enabled = False)
        self.shop_menu = Entity(parent = self, enabled = False)
        self.end_screen = Entity(parent = self, enabled = False)

        self.menus = [self.mainmenu, self.shop_menu]
        self.index = 0

        self.enable_end_screen = True

        # Animate the Menus
        for menu in (self.mainmenu, self.shop_menu):
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

            menu.on_enable = animate_in_menu

        self.mainmenu.enable()

        # Main Menu
        self.start_button = Button(text = "Start", color = colourH, highlight_color = colourH, scale_y = 0.1, scale_x = 0.3, y = 0.05, parent = self.mainmenu)
        self.shop_button = Button(text = "Shop", color = color.rgba(0, 0, 0, 0.7), highlight_color = color.rgba(0, 0, 0, 0.7), scale_y = 0.1, scale_x = 0.3, y = -0.07, parent = self.mainmenu)
        self.quit_button = Button(text = "Quit", color = color.rgba(0, 0, 0, 0.7), highlight_color = color.rgba(0, 0, 0, 0.7), scale_y = 0.1, scale_x = 0.3, y = -0.19, parent = self.mainmenu)

        invoke(setattr, self.start_button, "color", colourH, delay = 0.5)

        # Endscreen
        retry_text = Text("Retry", scale = 4, line_height = 2, x = 0, origin = 0, y = 0.1, z = -100, parent = self.end_screen)
        press_space = Text("Press Space", scale = 2, line_height = 2, x = 0, origin = 0, y = 0, z = -100, parent = self.end_screen)
        self.highscore_text = Text(text = str(self.player.highscore), origin = (0, 0), size = 0.05, scale = (0.8, 0.8), position = window.top - (0, 0.1), parent = self.end_screen, z = -100)
        camera.overlay.parent = self.end_screen
        camera.overlay.color = color.rgba(220, 0, 0, 100)

        # Shop Menu
        self.test = Text("test", parent = self.shop_menu, origin = 0)
        self.back_shop = Button(text = "Back", color = color.rgba(0, 0, 0, 0.7), highlight_color = color.rgba(0, 0, 0, 0.7), scale_y = 0.1, scale_x = 0.3, y = -0.19, parent = self.shop_menu)

    def update(self):
        if self.player.health <= 0:
            if self.enable_end_screen:
                self.end_screen.enable()
                self.enable_end_screen = False
                self.player.check_highscore()
                application.time_scale = 0.2
                self.player.dead = True
                self.highscore_text.text = "Highscore: " + str(self.player.highscore)

        if held_keys["space"] and not self.enable_end_screen:
            self.player.reset()
            self.end_screen.disable()
            self.enable_end_screen = True
            
    def input(self, key):
        if self.player.health <= 0:
            if key == "space":
                self.end_screen.disable()
                self.enable_end_screen = True
                self.player.reset()

        if key == "up arrow":
            for menu in self.menus:
                if menu.enabled:
                    self.index -= 1
                    if self.index <= -1:
                        self.index = 0
                    menu.children[self.index].color = colourH
                    menu.children[self.index].highlight_color = colourH
                    for button in menu.children:
                        if menu.children[self.index] != button:
                            button.color = color.rgba(0, 0, 0, 0.7)
                            button.highlight_color = color.rgba(0, 0, 0, 0.7)

        elif key == "down arrow":
            for menu in self.menus:
                if menu.enabled:
                    self.index += 1
                    if self.index > len(menu.children) - 1:
                        self.index = len(menu.children) - 1
                    menu.children[self.index].color = colourH
                    menu.children[self.index].highlight_color = colourH
                    for button in menu.children:
                        if menu.children[self.index] != button:
                            button.color = color.rgba(0, 0, 0, 0.7)
                            button.highlight_color = color.rgba(0, 0, 0, 0.7)

        if key == "enter":
            if self.mainmenu.enabled:
                if highlighted(self.start_button):
                    self.start()
                elif highlighted(self.shop_button):
                    self.shop_menu.enable()
                    self.mainmenu.disable()
                elif highlighted(self.quit_button):
                    application.quit()
            elif self.shop_menu.enabled:
                if highlighted(self.back_shop):
                    self.shop_menu.disable()
                    self.mainmenu.enable()

    def start(self):
        self.mainmenu.disable()
        for enemy in self.player.enemies:
            enemy.enable()
        self.player.enable()