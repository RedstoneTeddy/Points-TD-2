import data_class
import pygame as pg
import logging
import tile_map

class Win_Lose_screen:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj
        self.current_tile_zoom: int = 1

        self.original_images: dict[str, pg.Surface] = {
            "target_prio": pg.transform.scale2x(pg.image.load("images/hud/target_prio.png").convert_alpha()),
            "target_prio_hover": pg.transform.scale2x(pg.image.load("images/hud/target_prio_hover.png").convert_alpha())
        }

        self.images: dict[str, pg.Surface] = {}
        self.Scale_images(True)


    def Scale_images(self, force_scaling: bool = False) -> None:
        """
        Scales the images to the current tile-zoom-level
        """
        if self.data.tile_zoom != self.current_tile_zoom or force_scaling:
            for key in self.original_images.keys():
                img_size: tuple[int, int] = self.original_images[key].get_size()
                self.images[key] = pg.transform.scale(self.original_images[key], (self.data.tile_zoom*img_size[0], self.data.tile_zoom*img_size[1]))
            self.current_tile_zoom = self.data.tile_zoom

    def Check_win_condition(self) -> bool:
        """
        Checks if the player has won the game
        """
        if self.data.wave == self.data.win_wave:
            return True
        return False
    
    def Check_lose_condition(self) -> bool:
        """
        Checks if the player has lost the game
        """
        if self.data.health <= 0:
            return True
        return False
    


    def Show_lose_screen(self) -> None:
        self.Scale_images()

        self.tile_map_obj.Show_win_lose_background()

        left_right_offset: int = (self.data.screen_size[0] - (32*8*self.data.tile_zoom)) // 2
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        mouse_tile_pos: tuple[int, int] = self.tile_map_obj.Calculate_tile_pos_from_px_pos(mouse_pos, only_allow_map=False)

        self.data.Draw_text("You lost!", 15*self.data.tile_zoom, (255,0,0), (self.data.screen_size[0]//2-40*self.data.tile_zoom, 50*self.data.tile_zoom))
        self.data.Draw_text(f"You got until wave: {self.data.wave}", 8*self.data.tile_zoom, (255,150,150), (self.data.screen_size[0]//2-60*self.data.tile_zoom, 70*self.data.tile_zoom))

        # Menu Button
        menu_pos: tuple[int, int] = (12, 14)
        if mouse_tile_pos[0] >= menu_pos[0] and mouse_tile_pos[0] < menu_pos[0]+8 and mouse_tile_pos[1] >= menu_pos[1] and mouse_tile_pos[1] < menu_pos[1]+2:
            self.data.screen.blit(self.images["target_prio_hover"], (menu_pos[0]*self.data.tile_zoom*8 + left_right_offset, menu_pos[1]*self.data.tile_zoom*8))
            if pg.mouse.get_pressed()[0]:
                # Reset some variables
                # self.data.Reset_game_variables()
                logging.info("Returned to main menu from lose screen")
                self.data.Transition_black_window("main_menu")
        else:
            self.data.screen.blit(self.images["target_prio"], (menu_pos[0]*self.data.tile_zoom*8 + left_right_offset, menu_pos[1]*self.data.tile_zoom*8))
        self.data.Draw_text("Menu", 8*self.data.tile_zoom, (255,255,255), (menu_pos[0]*self.data.tile_zoom*8 + left_right_offset + 6*self.data.tile_zoom, menu_pos[1]*self.data.tile_zoom*8 + 4*self.data.tile_zoom))

        # Quit Button
        quit_pos: tuple[int, int] = (16, 14)
        if mouse_tile_pos[0] >= quit_pos[0] and mouse_tile_pos[0] < quit_pos[0]+8 and mouse_tile_pos[1] >= quit_pos[1] and mouse_tile_pos[1] < quit_pos[1]+2:
            self.data.screen.blit(self.images["target_prio_hover"], (quit_pos[0]*self.data.tile_zoom*8 + left_right_offset, quit_pos[1]*self.data.tile_zoom*8))
            if pg.mouse.get_pressed()[0]:
                self.data.run = False
                logging.info("Quit game from lose screen")
        else:
            self.data.screen.blit(self.images["target_prio"], (quit_pos[0]*self.data.tile_zoom*8 + left_right_offset, quit_pos[1]*self.data.tile_zoom*8))
        self.data.Draw_text("Quit", 8*self.data.tile_zoom, (255,150,150), (quit_pos[0]*self.data.tile_zoom*8 + left_right_offset + 6*self.data.tile_zoom, quit_pos[1]*self.data.tile_zoom*8 + 4*self.data.tile_zoom))




    def Show_win_screen(self) -> None:
        self.Scale_images()
        
        self.tile_map_obj.Show_win_lose_background()

        left_right_offset: int = (self.data.screen_size[0] - (32*8*self.data.tile_zoom)) // 2
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        mouse_tile_pos: tuple[int, int] = self.tile_map_obj.Calculate_tile_pos_from_px_pos(mouse_pos, only_allow_map=False)

        self.data.Draw_text("You won!", 15*self.data.tile_zoom, (100,255,100), (self.data.screen_size[0]//2-40*self.data.tile_zoom, 50*self.data.tile_zoom))
       
        # Menu Button
        menu_pos: tuple[int, int] = (12, 14)
        if mouse_tile_pos[0] >= menu_pos[0] and mouse_tile_pos[0] < menu_pos[0]+8 and mouse_tile_pos[1] >= menu_pos[1] and mouse_tile_pos[1] < menu_pos[1]+2:
            self.data.screen.blit(self.images["target_prio_hover"], (menu_pos[0]*self.data.tile_zoom*8 + left_right_offset, menu_pos[1]*self.data.tile_zoom*8))
            if pg.mouse.get_pressed()[0]:
                # Reset some variables
                # self.data.Reset_game_variables()
                logging.info("Returned to main menu from lose screen")
                self.data.Transition_black_window("main_menu")
        else:
            self.data.screen.blit(self.images["target_prio"], (menu_pos[0]*self.data.tile_zoom*8 + left_right_offset, menu_pos[1]*self.data.tile_zoom*8))
        self.data.Draw_text("Menu", 8*self.data.tile_zoom, (255,255,255), (menu_pos[0]*self.data.tile_zoom*8 + left_right_offset + 6*self.data.tile_zoom, menu_pos[1]*self.data.tile_zoom*8 + 4*self.data.tile_zoom))

        # Quit Button
        quit_pos: tuple[int, int] = (16, 14)
        if mouse_tile_pos[0] >= quit_pos[0] and mouse_tile_pos[0] < quit_pos[0]+8 and mouse_tile_pos[1] >= quit_pos[1] and mouse_tile_pos[1] < quit_pos[1]+2:
            self.data.screen.blit(self.images["target_prio_hover"], (quit_pos[0]*self.data.tile_zoom*8 + left_right_offset, quit_pos[1]*self.data.tile_zoom*8))
            if pg.mouse.get_pressed()[0]:
                self.data.run = False
                logging.info("Quit game from lose screen")
        else:
            self.data.screen.blit(self.images["target_prio"], (quit_pos[0]*self.data.tile_zoom*8 + left_right_offset, quit_pos[1]*self.data.tile_zoom*8))
        self.data.Draw_text("Quit", 8*self.data.tile_zoom, (255,150,150), (quit_pos[0]*self.data.tile_zoom*8 + left_right_offset + 6*self.data.tile_zoom, quit_pos[1]*self.data.tile_zoom*8 + 4*self.data.tile_zoom))



        
