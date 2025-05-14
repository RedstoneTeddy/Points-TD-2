import data_class
import pygame as pg
import logging
import tile_map

class Hud:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj
        self.current_tile_zoom: int = 1

        self.wave_button_pressed: bool = False

        self.original_hud_images: dict[str, pg.Surface] = {
            "wave_button0": pg.image.load("images/hud/wave_button0.png").convert_alpha(),
            "wave_button1": pg.image.load("images/hud/wave_button1.png").convert_alpha(),
            "wave_button2": pg.image.load("images/hud/wave_button2.png").convert_alpha(),
            "wave_button3": pg.image.load("images/hud/wave_button3.png").convert_alpha(),
            "wave_hover": pg.image.load("images/hud/wave_hover.png").convert_alpha()
        }

        self.hud_images: dict[str, pg.Surface] = {}
        self.Scale_hud_images(True)

    def Scale_hud_images(self, force_scaling: bool = False) -> None:
        """
        Scales the hud images to the current tile-zoom-level
        """
        if self.data.tile_zoom != self.current_tile_zoom or force_scaling:
            for key in self.original_hud_images.keys():
                img_size: tuple[int, int] = self.original_hud_images[key].get_size()
                self.hud_images[key] = pg.transform.scale(self.original_hud_images[key], (self.data.tile_zoom*img_size[0], self.data.tile_zoom*img_size[1]))
            self.current_tile_zoom = self.data.tile_zoom


    def Show_hud(self) -> None:
        self.Scale_hud_images()
        
        left_right_offset: int = (self.data.screen_size[0] - (32*8*self.data.tile_zoom)) // 2

        if not self.data.running_wave:
            pos: tuple[int, int] = (26, 15)
            self.data.screen.blit(self.hud_images["wave_button0"], (pos[0]*self.data.tile_zoom*8 + left_right_offset, pos[1]*self.data.tile_zoom*8))
        else: # Wave is running
            if self.data.fast_forward:
                if self.data.auto_wave:
                    pos: tuple[int, int] = (26, 15)
                    self.data.screen.blit(self.hud_images["wave_button3"], (pos[0]*self.data.tile_zoom*8 + left_right_offset, pos[1]*self.data.tile_zoom*8))
                else:
                    pos: tuple[int, int] = (26, 15)
                    self.data.screen.blit(self.hud_images["wave_button2"], (pos[0]*self.data.tile_zoom*8 + left_right_offset, pos[1]*self.data.tile_zoom*8))
            else:
                pos: tuple[int, int] = (26, 15)
                self.data.screen.blit(self.hud_images["wave_button1"], (pos[0]*self.data.tile_zoom*8 + left_right_offset, pos[1]*self.data.tile_zoom*8))

        
        if self.data.performance_saving_setting != "extreme":
            mouse_pos: tuple[int, int] = pg.mouse.get_pos()
            tile_pos: tuple[int, int] = self.tile_map_obj.Calculate_tile_pos_from_px_pos(mouse_pos, only_allow_map=False)
            if tile_pos[0] >= 26 and tile_pos[0] < 30 and tile_pos[1] >= 15 and tile_pos[1] < 17:
                self.data.screen.blit(self.hud_images["wave_hover"], (pos[0]*self.data.tile_zoom*8 + left_right_offset, pos[1]*self.data.tile_zoom*8))

        if pg.mouse.get_pressed()[0]:
            mouse_pos: tuple[int, int] = pg.mouse.get_pos()
            tile_pos: tuple[int, int] = self.tile_map_obj.Calculate_tile_pos_from_px_pos(mouse_pos, only_allow_map=False)
            if tile_pos[0] >= 26 and tile_pos[0] < 30 and tile_pos[1] >= 15 and tile_pos[1] < 17 and not self.wave_button_pressed:
                self.wave_button_pressed = True
                if not self.data.running_wave:
                    self.data.Next_wave()
                else:
                    if not self.data.fast_forward:
                        self.data.fast_forward = True
                    elif self.data.auto_wave:
                        self.data.auto_wave = False
                        self.data.fast_forward = False
                    else:
                        self.data.auto_wave = True
                        self.data.fast_forward = True
        else:
            self.wave_button_pressed = False

