import data_class
import pygame as pg
import logging
import tile_map

class Pause_screen:
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

        self.esc_pressed: bool = False


    def Scale_images(self, force_scaling: bool = False) -> None:
        """
        Scales the images to the current tile-zoom-level
        """
        if self.data.tile_zoom != self.current_tile_zoom or force_scaling:
            for key in self.original_images.keys():
                img_size: tuple[int, int] = self.original_images[key].get_size()
                self.images[key] = pg.transform.scale(self.original_images[key], (self.data.tile_zoom*img_size[0], self.data.tile_zoom*img_size[1]))
            self.current_tile_zoom = self.data.tile_zoom

    def Check_pause_toggle(self) -> None:
        """
        Checks if the pause menu should be toggled
        """
        if pg.key.get_pressed()[pg.K_ESCAPE]:
            if not self.esc_pressed:
                self.esc_pressed = True
                self.data.paused = not self.data.paused
                if self.data.paused:
                    logging.info("Game paused")
                else:
                    logging.info("Game unpaused")
        else:
            self.esc_pressed = False

    def Show_pause_screen(self) -> None:
        self.Scale_images()

        self.tile_map_obj.Show_win_lose_background()

        left_right_offset: int = (self.data.screen_size[0] - (32*8*self.data.tile_zoom)) // 2
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        mouse_tile_pos: tuple[int, int] = self.tile_map_obj.Calculate_tile_pos_from_px_pos(mouse_pos, only_allow_map=False)

        self.data.Draw_text("Game Paused", 15*self.data.tile_zoom, (255,255,0), (self.data.screen_size[0]//2-50*self.data.tile_zoom, 30*self.data.tile_zoom))
        self.data.Draw_text("Press ESC to resume", 8*self.data.tile_zoom, (255,255,255), (self.data.screen_size[0]//2-50*self.data.tile_zoom, 50*self.data.tile_zoom))
        self.data.Draw_text(f"Current Wave: {self.data.wave}", 8*self.data.tile_zoom, (255,255,255), (self.data.screen_size[0]//2-45*self.data.tile_zoom, 60*self.data.tile_zoom))
        self.data.Draw_text(f"Money: {self.data.money} $", 8*self.data.tile_zoom, (255,255,255), (self.data.screen_size[0]//2-40*self.data.tile_zoom, 70*self.data.tile_zoom))


        # Resume Button
        resume_pos: tuple[int, int] = (10, 14)
        if mouse_tile_pos[0] >= resume_pos[0] and mouse_tile_pos[0] < resume_pos[0]+4 and mouse_tile_pos[1] >= resume_pos[1] and mouse_tile_pos[1] < resume_pos[1]+2:
            self.data.screen.blit(self.images["target_prio_hover"], (resume_pos[0]*self.data.tile_zoom*8 + left_right_offset, resume_pos[1]*self.data.tile_zoom*8))
            if pg.mouse.get_pressed()[0]:
                # Reset some variables
                # self.data.Reset_game_variables()
                logging.info("Returned to game from pause screen")
                self.data.paused = False
        else:
            self.data.screen.blit(self.images["target_prio"], (resume_pos[0]*self.data.tile_zoom*8 + left_right_offset, resume_pos[1]*self.data.tile_zoom*8))
        self.data.Draw_text("Back", 8*self.data.tile_zoom, (255,255,255), (resume_pos[0]*self.data.tile_zoom*8 + left_right_offset + 6*self.data.tile_zoom, resume_pos[1]*self.data.tile_zoom*8 + 4*self.data.tile_zoom))

        # Menu Button
        menu_pos: tuple[int, int] = (14, 14)
        if mouse_tile_pos[0] >= menu_pos[0] and mouse_tile_pos[0] < menu_pos[0]+4 and mouse_tile_pos[1] >= menu_pos[1] and mouse_tile_pos[1] < menu_pos[1]+2:
            self.data.screen.blit(self.images["target_prio_hover"], (menu_pos[0]*self.data.tile_zoom*8 + left_right_offset, menu_pos[1]*self.data.tile_zoom*8))
            if pg.mouse.get_pressed()[0]:
                # Reset some variables
                # self.data.Reset_game_variables()
                logging.info("Returned to main menu from pause screen")
                self.data.Transition_black_window("main_menu")
        else:
            self.data.screen.blit(self.images["target_prio"], (menu_pos[0]*self.data.tile_zoom*8 + left_right_offset, menu_pos[1]*self.data.tile_zoom*8))
        self.data.Draw_text("Menu", 8*self.data.tile_zoom, (255,255,255), (menu_pos[0]*self.data.tile_zoom*8 + left_right_offset + 6*self.data.tile_zoom, menu_pos[1]*self.data.tile_zoom*8 + 4*self.data.tile_zoom))

        # Quit Button
        quit_pos: tuple[int, int] = (18, 14)
        if mouse_tile_pos[0] >= quit_pos[0] and mouse_tile_pos[0] < quit_pos[0]+4 and mouse_tile_pos[1] >= quit_pos[1] and mouse_tile_pos[1] < quit_pos[1]+2:
            self.data.screen.blit(self.images["target_prio_hover"], (quit_pos[0]*self.data.tile_zoom*8 + left_right_offset, quit_pos[1]*self.data.tile_zoom*8))
            if pg.mouse.get_pressed()[0]:
                self.data.run = False
                logging.info("Quit game from pause screen")
        else:
            self.data.screen.blit(self.images["target_prio"], (quit_pos[0]*self.data.tile_zoom*8 + left_right_offset, quit_pos[1]*self.data.tile_zoom*8))
        self.data.Draw_text("Quit", 8*self.data.tile_zoom, (255,150,150), (quit_pos[0]*self.data.tile_zoom*8 + left_right_offset + 6*self.data.tile_zoom, quit_pos[1]*self.data.tile_zoom*8 + 4*self.data.tile_zoom))


