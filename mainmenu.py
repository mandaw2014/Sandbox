from ursina import *

colourH = color.rgba(18, 152, 255, 180)

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

        invoke(self.mainmenu.enable, delay = 0.5)

        # Main Menu
        self.start_button = Button(text = "Start", color = colourH, highlight_color = color.rgba(0, 0, 0, 0.7), scale_y = 0.1, scale_x = 0.3, y = 0.05, parent = self.mainmenu)
        self.shop_button = Button(text = "Shop", color = color.rgba(0, 0, 0, 0.7), highlight_color = color.rgba(0, 0, 0, 0.7), scale_y = 0.1, scale_x = 0.3, y = -0.07, parent = self.mainmenu)
        self.quit_button = Button(text = "Quit", color = color.rgba(0, 0, 0, 0.7), highlight_color = color.rgba(0, 0, 0, 0.7), scale_y = 0.1, scale_x = 0.3, y = -0.19, parent = self.mainmenu)

        invoke(setattr, self.start_button, "color", colourH, delay = 0.1)

        # Shop Menu
        self.test = Text("test", parent = self.shop_menu, origin = 0)
        self.back_shop = Button(text = "Back", color = color.rgba(0, 0, 0, 0.7), highlight_color = color.rgba(0, 0, 0, 0.7), scale_y = 0.1, scale_x = 0.3, y = -0.19, parent = self.shop_menu)

    def update(self):
        if self.player.health <= 0:
            if self.enable_end_screen:
                self.end_screen.enable()
                self.enable_end_screen = False
            
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
                if self.start_button.color == colourH:
                    self.start()
                elif self.shop_button.color == colourH:
                    self.shop_menu.enable()
                    self.mainmenu.disable()
                elif self.quit_button.color == colourH:
                    application.quit()
            elif self.shop_menu.enabled:
                if self.back_shop.color == colourH:
                    self.shop_menu.disable()
                    self.mainmenu.enable()

    def start(self):
        self.mainmenu.disable()
        for enemy in self.player.enemies:
            enemy.enable()
        self.player.enable()