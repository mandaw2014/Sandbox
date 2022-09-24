from gettext import install
from ursina import *
from ursina import curve

colourH = color.rgba(18, 152, 255, 180)
colourN = color.rgba(0, 0, 0, 0.7)
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
        self.end_screen = Entity(parent = self, enabled = False)
        self.pause_menu = Entity(parent = self, enabled = False)
        self.abilities_menu = Entity(parent = self, enabled = False)

        self.menus = [self.mainmenu, self.pause_menu, self.abilities_menu]
        self.index = 0

        self.enable_end_screen = True

        # Animate the Menus
        for menu in (self.mainmenu, self.abilities_menu):
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
        self.ability_button = Button(text = "Abilities", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = -0.07, parent = self.mainmenu)
        self.quit_button = Button(text = "Quit", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = -0.19, parent = self.mainmenu)

        invoke(setattr, self.start_button, "color", colourH, delay = 0.5)

        # Endscreen
        retry_text = Text("Retry", scale = 4, line_height = 2, x = 0, origin = 0, y = 0.1, z = -100, parent = self.end_screen)
        press_space = Text("Press Enter", scale = 2, line_height = 2, x = 0, origin = 0, y = 0, z = -100, parent = self.end_screen)
        self.highscore_text = Text(text = str(self.player.highscore), origin = (0, 0), size = 0.05, scale = (0.8, 0.8), position = window.top - (0, 0.1), parent = self.end_screen, z = -100)
        camera.overlay.parent = self.end_screen
        camera.overlay.color = color.rgba(220, 0, 0, 100)

        # Pause Menu
        self.resume_button = Button(text = "Resume", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = 0.05, parent = self.pause_menu)
        self.retry_button = Button(text = "Retry", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = -0.07, parent = self.pause_menu)
        self.mainmenu_button = Button(text = "Main Menu", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = -0.19, parent = self.pause_menu)
        self.pause_overlay = Entity(parent = self.pause_menu, model = "quad", scale = 99, color = color.rgba(20, 20, 20, 100), eternal = True, z = 10)

        # Ability Menu
        self.rope_button = AbilityItem("Rope", "rope-icon", menu = self.abilities_menu, position = (0, 0.2))
        self.dashing_button = AbilityItem("Dashing", "dash-icon.png", menu = self.abilities_menu, position = (0, 0.05), icon_scale = (0.5, 0.4))
        self.slomo_button = AbilityItem("Slo-Motion", "slomo.png", menu = self.abilities_menu, position = (0, -0.1), equiped_text = "unequipped")
        self.back_ability = Button(text = "Back", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = -0.25, parent = self.abilities_menu)
        
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
                elif highlighted(self.ability_button):
                    self.abilities_menu.enable()
                    self.mainmenu.disable()
                    self.update_menu(self.abilities_menu)
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

            # Ability menu
            elif self.abilities_menu.enabled:
                if highlighted(self.back_ability):
                    self.abilities_menu.disable()
                    self.mainmenu.enable()
                    self.update_menu(self.mainmenu)
                elif highlighted(self.rope_button):
                    self.equip_ability(self.player.rope, self.rope_button, self.player.primary_abilities)
                elif highlighted(self.dashing_button):
                    self.equip_ability(self.player.dash_ability, self.dashing_button, self.player.secondary_abilities)
                elif highlighted(self.slomo_button):
                    self.equip_ability(self.player.slow_motion, self.slomo_button, self.player.secondary_abilities)

            # End Screen
            if self.player.health <= 0:
                self.end_screen.disable()
                self.enable_end_screen = True
                self.player.reset()

        # Pause Menu
        if key == "escape":
            if self.player.enabled:
                self.pause()
                self.update_menu(self.pause_menu)

    def start(self):
        self.mainmenu.disable()
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

    def equip_ability(self, ability, ability_button, abilities_list):
        if ability.ability_enabled:
            ability.ability_enabled = False
            ability_button.equiped_text.text = "unequipped"
        else:
            if all(not a.ability_enabled for a in abilities_list):
                ability.ability_enabled = True
                ability_button.equiped_text.text = "equipped"
            else:
                ability_button.shake()

class AbilityItem(Button):
    def __init__(self, text, icon, menu, position = (0, 0), icon_scale = (0.4, 0.4), equiped_text = "equiped", **kwargs):
        super().__init__(
            parent = menu,
            text = text,
            position = position,
            color = colourN,
            highlight_color = colourN,
            scale_y = 0.14, 
            scale_x = 0.16,
            **kwargs
        )

        self.icon_ = Entity(model = "quad", texture = icon, parent = self, scale = icon_scale, y = -0.08)
        self.equiped_text = Text(parent = self, text = equiped_text, scale = 4, y = -0.35, origin = 0)
        self.text_entity.y = 0.3