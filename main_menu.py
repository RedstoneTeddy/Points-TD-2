import data_class
import pygame as pg
import easygui



class Main_menu:
    def __init__(self, data: data_class.Data_class) -> None:
        self.data: data_class.Data_class = data

        self.button_pressed: bool = False


        


    def Render_main(self) -> None:
        self.data.Draw_text("Points TD 2", 10 * self.data.hud_zoom, (255, 255, 255), (self.data.screen_size[0]//2 - 35*self.data.hud_zoom, 30*self.data.hud_zoom))


        # Credentials
        self.data.Draw_text("Created by: Redstone_Teddy", 7* self.data.hud_zoom, (255, 150, 0), (self.data.hud_zoom ,self.data.screen_size[1] - 8*self.data.hud_zoom))
        self.data.Draw_text(f"Version: {self.data.version}", 6* self.data.hud_zoom, (255, 255, 255), (self.data.hud_zoom ,self.data.screen_size[1] - 14*self.data.hud_zoom))

        # Easy Button
        easy_button = pg.Rect(self.data.screen_size[0]//2 - 25*self.data.hud_zoom, 50*self.data.hud_zoom, 50*self.data.hud_zoom, 20*self.data.hud_zoom)
        pg.draw.rect(self.data.screen, (100, 100, 100), easy_button)
        pg.draw.rect(self.data.screen, (0, 150, 0), easy_button, 2)
        if easy_button.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(self.data.screen, (0, 255, 0), easy_button, 2)
            self.data.Draw_text("Easy", 10 * self.data.hud_zoom, (0, 255, 0), (self.data.screen_size[0]//2 - 20*self.data.hud_zoom, 55*self.data.hud_zoom))
            if pg.mouse.get_pressed()[0] and not self.button_pressed and not self.data.ongoing_transition:
                self.button_pressed = True
                self.data.difficulty = "easy"
                self.data.Transition_black_window("map_select")
        else:
            self.data.Draw_text("Easy", 10 * self.data.hud_zoom, (255, 255, 255), (self.data.screen_size[0]//2 - 20*self.data.hud_zoom, 55*self.data.hud_zoom))
                
        # Medium Button
        medium_button = pg.Rect(self.data.screen_size[0]//2 - 25*self.data.hud_zoom, 75*self.data.hud_zoom, 50*self.data.hud_zoom, 20*self.data.hud_zoom)
        pg.draw.rect(self.data.screen, (100, 100, 100), medium_button)
        pg.draw.rect(self.data.screen, (150, 80, 0), medium_button, 2)
        if medium_button.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(self.data.screen, (250, 150, 0), medium_button, 2)
            self.data.Draw_text("Medium", 10 * self.data.hud_zoom, (250, 150, 0), (self.data.screen_size[0]//2 - 20*self.data.hud_zoom, 80*self.data.hud_zoom))
            if pg.mouse.get_pressed()[0] and not self.button_pressed and not self.data.ongoing_transition:
                self.button_pressed = True
                self.data.difficulty = "medium"
                self.data.Transition_black_window("map_select")
        else:
            self.data.Draw_text("Medium", 10 * self.data.hud_zoom, (255, 255, 255), (self.data.screen_size[0]//2 - 20*self.data.hud_zoom, 80*self.data.hud_zoom))

        # Hard Button
        hard_button = pg.Rect(self.data.screen_size[0]//2 - 25*self.data.hud_zoom, 100*self.data.hud_zoom, 50*self.data.hud_zoom, 20*self.data.hud_zoom)
        pg.draw.rect(self.data.screen, (100, 100, 100), hard_button)
        pg.draw.rect(self.data.screen, (200, 0, 0), hard_button, 2)
        if hard_button.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(self.data.screen, (255, 100, 100), hard_button, 2)
            self.data.Draw_text("Hard", 10 * self.data.hud_zoom, (255, 100, 100), (self.data.screen_size[0]//2 - 20*self.data.hud_zoom, 105*self.data.hud_zoom))
            if pg.mouse.get_pressed()[0] and not self.button_pressed and not self.data.ongoing_transition:
                self.button_pressed = True
                self.data.difficulty = "hard"
                self.data.Transition_black_window("map_select")
        else:
            self.data.Draw_text("Hard", 10 * self.data.hud_zoom, (255, 255, 255), (self.data.screen_size[0]//2 - 20*self.data.hud_zoom, 105*self.data.hud_zoom))

        # Specials Button
        specials_button = pg.Rect(self.data.screen_size[0]//2 - 25*self.data.hud_zoom, 125*self.data.hud_zoom, 50*self.data.hud_zoom, 20*self.data.hud_zoom)
        pg.draw.rect(self.data.screen, (100, 100, 100), specials_button)
        pg.draw.rect(self.data.screen, (100, 0, 0), specials_button, 2)
        if specials_button.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(self.data.screen, (150, 0, 0), specials_button, 2)
            self.data.Draw_text("Specials", 10 * self.data.hud_zoom, (150, 0, 0), (self.data.screen_size[0]//2 - 24*self.data.hud_zoom, 130*self.data.hud_zoom))
            if pg.mouse.get_pressed()[0] and not self.button_pressed and not self.data.ongoing_transition:
                self.button_pressed = True
                selected_special = easygui.choicebox("Select a special challenge:", "Specials", ["Back", "Hacker", "Inflation", "Late to the Party"])
                if selected_special == "Back":
                    return
                elif selected_special == "Hacker":
                    self.data.difficulty = "hacker"
                    self.data.Transition_black_window("map_select")
                elif selected_special == "Inflation":
                    self.data.difficulty = "inflation"
                    self.data.Transition_black_window("map_select")
                elif selected_special == "Late to the Party":
                    self.data.difficulty = "late_to_the_party"
                    self.data.Transition_black_window("map_select")
                else:
                    return
                
        else:
            self.data.Draw_text("Specials", 10 * self.data.hud_zoom, (255, 255, 255), (self.data.screen_size[0]//2 - 24*self.data.hud_zoom, 130*self.data.hud_zoom))
        




        if pg.mouse.get_pressed()[0] == 0:
            self.button_pressed = False
            
            
        





